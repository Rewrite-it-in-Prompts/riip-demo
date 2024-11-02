package main

type Message struct {
  Role    string `json:"role"`
  Content string `json:"content"`
}

type Config struct {
  Models        []string  `yaml:"models"`
  DefaultModel  int       `yaml:"default_model"`
  BasePrompt    []Message `yaml:"base_prompt"`
  Templates     struct {
    SystemPrompts map[string]string `yaml:"system_prompts"`
    UserPrompts   map[string]string `yaml:"user_prompts"`
  } `yaml:"templates"`
  AWS struct {
    Region        string `yaml:"region"`
    ReadTimeout   int    `yaml:"read_timeout"`
    ConnectTimeout int   `yaml:"connect_timeout"`
  } `yaml:"aws"`
}

type Architecture struct {
  Vision   string     `yaml:"vision"`
  FileList []FileInfo `yaml:"filelist"`
}

type FileInfo struct {
  Path        string `yaml:"path"`
  Description string `yaml:"description"`
  Content     string `yaml:"content,omitempty"`
}

type Implementation struct {
  Notes    string     `yaml:"implementation-notes"`
  FileList []FileInfo `yaml:"filelist"`
}
