use std::path::PathBuf;
use std::env;

#[derive(Debug)]
pub struct Args {
    pub input_files: Vec<String>,
    pub output_dir: PathBuf,
    pub language: String,
    pub execute: Vec<String>,
    pub max_retries: u32,
}

pub fn parse_args() -> Args {
    let args: Vec<String> = env::args().collect();
    let mut input_files = Vec::new();
    let mut output_dir = PathBuf::new();
    let mut language = String::from("python");
    let mut execute = Vec::new();
    let mut max_retries = 1;
    
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-o" | "--output" => {
                i += 1;
                output_dir = PathBuf::from(&args[i]);
            }
            "-l" | "--language" => {
                i += 1;
                language = args[i].clone();
            }
            "-x" | "--execute" => {
                i += 1;
                execute.push(args[i].clone());
            }
            "-n" | "--max-retries" => {
                i += 1;
                max_retries = args[i].parse().unwrap_or(1);
            }
            _ => input_files.push(args[i].clone()),
        }
        i += 1;
    }

    if output_dir.as_os_str().is_empty() {
        eprintln!("Error: Output directory (-o) is required");
        std::process::exit(1);
    }

    if input_files.is_empty() {
        eprintln!("Error: At least one input file is required");
        std::process::exit(1);
    }

    Args {
        input_files,
        output_dir,
        language,
        execute,
        max_retries,
    }
}
