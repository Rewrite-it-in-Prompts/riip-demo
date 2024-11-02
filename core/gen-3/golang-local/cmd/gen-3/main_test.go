package main

import (
  "os"
  "path/filepath"
  "testing"
)

func TestBasicGeneration(t *testing.T) {
  tmpDir, err := os.MkdirTemp("", "gen3-test-*")
  if err != nil {
    t.Fatal(err)
  }
  defer os.RemoveAll(tmpDir)

  input := `package main

import "fmt"

func main() {
  fmt.Println("Hello")
}`

  inputFile := filepath.Join(tmpDir, "input.go")
  if err := os.WriteFile(inputFile, []byte(input), 0644); err != nil {
    t.Fatal(err)
  }

  outputDir := filepath.Join(tmpDir, "output")
  args := &Args{
    inputFiles: []string{inputFile},
    outputDir:  outputDir,
    language:   "go",
    maxRetries: 1,
    configPath: "prompt_config.yaml",
  }

  chat, err := NewCodingChat(args.configPath)
  if err != nil {
    t.Fatal(err)
  }

  generator := NewGenerator(chat, args)
  inputContent, err := readInputFiles(args.inputFiles)
  if err != nil {
    t.Fatal(err)
  }

  if err := generator.Generate(inputContent); err != nil {
    t.Fatal(err)
  }

  if _, err := os.Stat(filepath.Join(outputDir, "architecture.yaml")); err != nil {
    t.Error("architecture.yaml not created")
  }
}