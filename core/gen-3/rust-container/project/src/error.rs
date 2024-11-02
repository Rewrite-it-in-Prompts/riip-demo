use std::fmt;
use aws_sdk_bedrockruntime::error::SdkError;
use aws_sdk_bedrockruntime::operation::invoke_model::InvokeModelError;

#[derive(Debug)]
pub enum Error {
    Io(std::io::Error),
    Yaml(serde_yaml::Error),
    Json(serde_json::Error),
    Aws(aws_sdk_bedrockruntime::Error),
    AwsSdk(SdkError<InvokeModelError>),
    MaxRetries,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Io(e) => write!(f, "IO error: {}", e),
            Error::Yaml(e) => write!(f, "YAML error: {}", e),
            Error::Json(e) => write!(f, "JSON error: {}", e),
            Error::Aws(e) => write!(f, "AWS error: {}", e),
            Error::AwsSdk(e) => write!(f, "AWS SDK error: {}", e),
            Error::MaxRetries => write!(f, "Maximum retries reached"),
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Self {
        Error::Io(err)
    }
}

impl From<serde_yaml::Error> for Error {
    fn from(err: serde_yaml::Error) -> Self {
        Error::Yaml(err)
    }
}

impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Self {
        Error::Json(err)
    }
}

impl From<aws_sdk_bedrockruntime::Error> for Error {
    fn from(err: aws_sdk_bedrockruntime::Error) -> Self {
        Error::Aws(err)
    }
}

impl From<SdkError<InvokeModelError>> for Error {
    fn from(err: SdkError<InvokeModelError>) -> Self {
        Error::AwsSdk(err)
    }
}