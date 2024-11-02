use crate::args::Args;
use crate::chat::CodingChat;
use crate::error::Error;
use crate::execute::execute_pipeline;
use crate::files::{get_file_extension, scan_output_directory};
use crate::types::{Architecture, FileInfo};
use crate::yaml::{generate_architecture, process_resumption, handle_error};
use std::fs;
use std::path::Path;

pub async fn generate_code(chat: &CodingChat, input_text: &str, args: &Args) -> Result<(), Error> {
    fs::create_dir_all(&args.output_dir)?;
    let arch_path = args.output_dir.join("architecture.yaml");
    
    let arch_data = if arch_path.exists() {
        eprintln!("{}: Found existing architecture.yaml", chat.session);
        let arch_str = fs::read_to_string(&arch_path)?;
        let arch: Architecture = serde_yaml::from_str(&arch_str)?;
        
        let target_exts: Vec<String> = arch.filelist.iter()
            .map(|f| get_file_extension(&f.path))
            .collect();
        
        let existing_files = scan_output_directory(&args.output_dir, &target_exts)?;
        
        let outputs = execute_pipeline(args, &args.output_dir).await?;
        let pipeline_summary = outputs.iter()
            .enumerate()
            .map(|(i, (stdout, stderr, rc))| {
                format!("cmd{}: stdout={} stderr={} rc={}", i, stdout, stderr, rc)
            })
            .collect::<Vec<_>>()
            .join("\n");
        
        process_resumption(chat, input_text, &arch, &existing_files, &pipeline_summary).await?
    } else {
        eprintln!("{}: Generating new architecture", chat.session);
        let arch = generate_architecture(chat, input_text).await?;
        fs::write(&arch_path, serde_yaml::to_string(&arch)?)?;
        arch
    };

    let mut retry_count = 0;
    while retry_count <= args.max_retries {
        for file_info in &arch_data.filelist {
            let file_path = args.output_dir.join(&file_info.path);
            if let Some(parent) = file_path.parent() {
                fs::create_dir_all(parent)?;
            }
            
            eprintln!("{}: Generating {}", chat.session, file_info.path);
            let content = generate_file(chat, file_info, &arch_data).await?;
            
            fs::write(&file_path, content)?;
            eprintln!("{}: Wrote {}", chat.session, file_info.path);
        }
        
        if !args.execute.is_empty() {
            let outputs = execute_pipeline(args, &args.output_dir).await?;
            for (i, (stdout, stderr, rc)) in outputs.iter().enumerate() {
                let cmd = &args.execute[i];
                eprintln!("{}: Executed '{}', rc={}", chat.session, cmd, rc);
                if *rc != 0 {
                    let error_data = handle_error(chat, &format!(
                        "Command '{}' failed:\n{}\n{}", cmd, stdout, stderr
                    )).await?;
                    fs::write(
                        args.output_dir.join("implementation.yaml"),
                        serde_yaml::to_string(&error_data)?
                    )?;
                    retry_count += 1;
                    continue;
                }
            }
            eprintln!("{}: All commands succeeded", chat.session);
            return Ok(());
        }
        return Ok(());
    }
    
    eprintln!("{}: Max retries reached", chat.session);
    Err(Error::MaxRetries)
}

async fn generate_file(chat: &CodingChat, file_info: &FileInfo, arch_data: &Architecture) 
    -> Result<String, Error> {
    if let Some(content) = &file_info.content {
        return Ok(content.clone());
    }
    
    let system_prompt = format!(
        "Generate code for {}\nDescription: {}\nProject vision: {}",
        file_info.path, file_info.description, arch_data.vision
    );

    let (code, _, _, _) = chat.invoke(
        &system_prompt,
        "Generate the file content",
        &get_file_extension(&file_info.path)
    ).await?;
    
    Ok(code)
}
