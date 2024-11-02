use crate::aws_client::create_client;
use crate::error::Error;
use aws_sdk_bedrockruntime::primitives::Blob;
use serde::{Deserialize, Serialize};
use std::time::Instant;
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct CodingChat {
    pub session: String,
    pub model: String,
    pub messages: Vec<Message>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Message {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize)]
struct RequestConfig {
    system: String,
    messages: Vec<Message>,
}

impl Default for RequestConfig {
    fn default() -> Self {
        Self {
            system: String::new(),
            messages: Vec::new(),
        }
    }
}

impl CodingChat {
    pub async fn new() -> Self {
        Self {
            session: Uuid::new_v4().to_string(),
            model: "anthropic.claude-v2".to_string(),
            messages: Vec::new(),
        }
    }

    pub async fn invoke(&mut self, system_prompt: &str, user_prompt: &str, filetype: &str) 
        -> Result<(String, String, String, i32), Error> {
        
        let config = RequestConfig {
            system: system_prompt.to_string(),
            messages: self.messages.clone(),
        };

        let client = create_client().await;
        let json_body = serde_json::to_string(&config)?;
        let blob = Blob::new(json_body.as_bytes());
        
        let response = client
            .invoke_model()
            .model_id(&self.model)
            .body(blob)
            .send()
            .await?;

        let response_body: Message = serde_json::from_slice(&response.body.as_ref())?;
        
        self.messages.push(Message {
            role: "user".to_string(),
            content: user_prompt.to_string(),
        });
        self.messages.push(response_body.clone());

        Ok((
            response_body.content,
            String::new(),
            String::new(),
            0,
        ))
    }
}
