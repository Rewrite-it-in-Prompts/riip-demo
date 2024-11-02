use aws_sdk_bedrockruntime::{Client, Config};
use aws_config::timeout::TimeoutConfig;
use aws_types::region::Region;
use std::time::Duration;

pub async fn create_client() -> Client {
    let timeout_config = TimeoutConfig::builder()
        .connect_timeout(Duration::from_secs(300))
        .read_timeout(Duration::from_secs(600))
        .build();
    
    let config = aws_config::from_env()
        .region(Region::new("us-west-2"))
        .timeout_config(timeout_config)
        .load()
        .await;
        
    Client::new(&config)
}
