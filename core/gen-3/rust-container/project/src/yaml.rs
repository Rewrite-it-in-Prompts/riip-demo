use crate::chat::CodingChat;
use crate::error::Error;
use crate::types::{Architecture, FileInfo};
use std::collections::HashMap;

pub async fn generate_architecture(chat: &CodingChat, input_text: &str) 
    -> Result<Architecture, Error> {
    let system_prompt = r#"You are a software architect. Generate architecture.yaml for a multi-file project.
Example format:
vision: |
  Project requirements and specifications
filelist:
  - path: src/main.py
    description: Main entry point
    content: |
      print('hello')  # Optional, for small files
  - path: src/lib.py
    description: Core functionality"#;

    let (yaml_str, _, _, _) = chat.invoke(
        system_prompt,
        &format!("Generate architecture for:\n{}", input_text),
        "yaml"
    ).await?;
    
    Ok(serde_yaml::from_str(&yaml_str)?)
}

pub async fn process_resumption(
    chat: &CodingChat,
    input_text: &str,
    arch_data: &Architecture,
    existing_files: &HashMap<String, String>,
    pipeline_output: &str,
) -> Result<Architecture, Error> {
    let system_prompt = r#"Review project state and generate YAML response:
vision: |
  Project status and needed changes
filelist: []  # Empty if no changes needed, else same format as architecture.yaml"#;

    let user_prompt = format!(
        "Input:\n{}\nCurrent architecture: {}\nFiles generated: {}\nPipeline output: {}",
        input_text,
        serde_yaml::to_string(arch_data)?,
        serde_yaml::to_string(existing_files)?,
        pipeline_output
    );

    let (yaml_str, _, _, _) = chat.invoke(system_prompt, &user_prompt, "yaml").await?;
    
    Ok(serde_yaml::from_str(&yaml_str)?)
}

pub async fn handle_error(chat: &CodingChat, error_msg: &str) -> Result<Architecture, Error> {
    let system_prompt = r#"Generate YAML response for error:
implementation-notes: |
  Error analysis and fix strategy
filelist:
  - path: file/to/fix.py
    description: Fix description
    content: |
      Fixed code"#;

    let (yaml_str, _, _, _) = chat.invoke(
        system_prompt,
        &format!("Fix error:\n{}", error_msg),
        "yaml"
    ).await?;
    
    Ok(serde_yaml::from_str(&yaml_str)?)
}