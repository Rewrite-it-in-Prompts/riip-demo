package main

import (
  "context"
  "encoding/json"
  "fmt"
  "time"

  "github.com/aws/aws-sdk-go-v2/service/bedrockruntime"
)

type CodingChat struct {
  messages []Message
  model    string
  session  string
  client   *bedrockruntime.Client
  config   *Config
}

func NewCodingChat(configPath string) (*CodingChat, error) {
  config, err := loadConfig(configPath)
  if err != nil {
    return nil, err
  }

  client, err := newBedrockClient(config)
  if err != nil {
    return nil, err
  }

  session := fmt.Sprintf("%s/%s", 
    time.Now().Format("2006-01-02/15_04"),
    generateSessionID())

  return &CodingChat{
    messages: config.BasePrompt,
    model:    config.Models[config.DefaultModel],
    session:  session,
    client:   client,
    config:   config,
  }, nil
}

func (c *CodingChat) Invoke(ctx context.Context, userPrompt, fileType, systemPrompt string) (string, error) {
  if systemPrompt == "" {
    var ok bool
    systemPrompt, ok = c.config.Templates.SystemPrompts[fileType]
    if !ok {
      systemPrompt = c.config.Templates.SystemPrompts["default"]
    }
  }

  c.messages = append(c.messages, Message{
    Role:    "user",
    Content: userPrompt,
  })

  input := struct {
    Messages []Message `json:"messages"`
    System  string    `json:"system"`
  }{
    Messages: c.messages,
    System:   systemPrompt,
  }

  payload, err := json.Marshal(input)
  if err != nil {
    return "", err
  }

  resp, err := c.client.InvokeModel(ctx, &bedrockruntime.InvokeModelInput{
    ModelId: &c.model,
    Body:    payload,
  })
  if err != nil {
    return "", err
  }

  var result struct {
    Content []struct {
      Text string `json:"text"`
    } `json:"content"`
  }
  if err := json.Unmarshal(resp.Body, &result); err != nil {
    return "", err
  }

  content := result.Content[0].Text
  c.messages = append(c.messages, Message{
    Role:    "assistant",
    Content: content,
  })

  return content, nil
}
