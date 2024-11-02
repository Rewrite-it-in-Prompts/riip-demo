use crate::error::Error;
use std::collections::HashMap;
use std::fs;
use std::path::Path;

pub fn read_input_files(paths: &[String]) -> Result<String, Error> {
    let mut combined = Vec::new();
    
    for path in paths {
        let content = if path == "-" {
            use std::io::{self, Read};
            let mut buffer = String::new();
            io::stdin().read_to_string(&mut buffer)?;
            buffer
        } else {
            fs::read_to_string(path)?
        };
        combined.push(content);
    }
    
    Ok(combined.join("\n"))
}

pub fn get_file_extension(path: &str) -> String {
    Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|s| s.to_lowercase())
        .unwrap_or_default()
}

pub fn scan_output_directory(dir: &Path, target_exts: &[String]) 
    -> Result<HashMap<String, String>, Error> {
    let mut files = HashMap::new();
    
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() {
            if let Some(ext) = path.extension() {
                if let Some(ext_str) = ext.to_str() {
                    if target_exts.contains(&ext_str.to_lowercase()) {
                        let rel_path = path.strip_prefix(dir)
                            .unwrap()
                            .to_string_lossy()
                            .into_owned();
                        let content = fs::read_to_string(&path)?;
                        files.insert(rel_path, content);
                    }
                }
            }
        }
    }
    
    Ok(files)
}
