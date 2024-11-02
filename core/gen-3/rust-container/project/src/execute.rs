use crate::args::Args;
use crate::error::Error;
use std::path::Path;
use tokio::process::Command;
use tokio::io::{BufReader, AsyncBufReadExt};

pub async fn execute_pipeline(args: &Args, cwd: &Path) 
    -> Result<Vec<(String, String, i32)>, Error> {
    let mut outputs = Vec::new();
    
    for cmd in &args.execute {
        let mut child = Command::new("sh")
            .arg("-c")
            .arg(cmd)
            .current_dir(cwd)
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()?;
        
        let stdout = child.stdout.take().unwrap();
        let stderr = child.stderr.take().unwrap();
        
        let mut stdout_lines = BufReader::new(stdout).lines();
        let mut stderr_lines = BufReader::new(stderr).lines();
        
        let mut stdout_data = Vec::new();
        let mut stderr_data = Vec::new();
        
        loop {
            tokio::select! {
                result = stdout_lines.next_line() => {
                    match result {
                        Ok(Some(line)) => {
                            println!("{}", line);
                            stdout_data.push(line);
                        }
                        Ok(None) => break,
                        Err(e) => return Err(Error::Io(e)),
                    }
                }
                result = stderr_lines.next_line() => {
                    match result {
                        Ok(Some(line)) => {
                            eprintln!("{}", line);
                            stderr_data.push(line);
                        }
                        Ok(None) => break,
                        Err(e) => return Err(Error::Io(e)),
                    }
                }
            }
        }
        
        let status = child.wait().await?;
        
        outputs.push((
            stdout_data.join("\n"),
            stderr_data.join("\n"),
            status.code().unwrap_or(-1),
        ));
    }
    
    Ok(outputs)
}
