use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Architecture {
    pub vision: String,
    pub filelist: Vec<FileInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileInfo {
    pub path: String,
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content: Option<String>,
}
