package main

import (
  "context"
  "net/http"
  "time"

  "github.com/aws/aws-sdk-go-v2/aws"
  "github.com/aws/aws-sdk-go-v2/config"
  "github.com/aws/aws-sdk-go-v2/service/bedrockruntime"
)

func newBedrockClient(cfg *Config) (*bedrockruntime.Client, error) {
  awsCfg, err := config.LoadDefaultConfig(context.Background(),
    config.WithRegion(cfg.AWS.Region),
    config.WithClientLogMode(aws.LogRequestWithBody|aws.LogResponseWithBody),
    config.WithHTTPClient(newHTTPClient(cfg)),
  )
  if err != nil {
    return nil, err
  }
  return bedrockruntime.NewFromConfig(awsCfg), nil
}

func newHTTPClient(cfg *Config) *http.Client {
  return &http.Client{
    Timeout: time.Duration(cfg.AWS.ReadTimeout) * time.Second,
    Transport: &http.Transport{
      ResponseHeaderTimeout: time.Duration(cfg.AWS.ConnectTimeout) * time.Second,
    },
  }
}
