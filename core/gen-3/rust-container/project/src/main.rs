mod args;
mod aws_client;
mod chat;
mod code_gen;
mod error;
mod execute;
mod files;
mod types;
mod yaml;

use crate::args::parse_args;
use crate::chat::CodingChat;
use crate::code_gen::generate_code;
use crate::files::read_input_files;
use std::process;

#[tokio::main]
async fn main() {
    let args = parse_args();
    let chat = CodingChat::new().await;
    
    eprintln!("Started {} {:?}", env!("CARGO_PKG_NAME"), args);
    
    let input_text = match read_input_files(&args.input_files) {
        Ok(text) => text,
        Err(e) => {
            eprintln!("Error reading input files: {}", e);
            process::exit(1);
        }
    };

    if let Err(e) = generate_code(&chat, &input_text, &args).await {
        eprintln!("Error: {}", e);
        process::exit(1);
    }
}
