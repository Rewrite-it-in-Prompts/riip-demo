package main

import (
  "fmt"
  "os"
)

func main() {
  args := parseArgs()
  
  chat, err := NewCodingChat(args.configPath)
  if err != nil {
    fmt.Fprintf(os.Stderr, "Error creating chat client: %v\n", err)
    os.Exit(1)
  }

  input, err := readInputFiles(args.inputFiles)
  if err != nil {
    fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
    os.Exit(1)
  }

  generator := NewGenerator(chat, args)
  if err := generator.Generate(input); err != nil {
    fmt.Fprintf(os.Stderr, "Generation failed: %v\n", err)
    os.Exit(1)
  }
}