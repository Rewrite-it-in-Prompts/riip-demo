package main

import (
  "fmt"
  "io"
  "os"
  "os/exec"
  "strings"
  "time"

  "gopkg.in/yaml.v3"
)

func generateSessionID() string {
  return fmt.Sprintf("%x", time.Now().UnixNano())
}

func loadConfig(path string) (*Config, error) {
  f, err := os.Open(path)
  if err != nil {
    return nil, err
  }
  defer f.Close()

  var config Config
  if err := yaml.NewDecoder(f).Decode(&config); err != nil {
    return nil, err
  }
  return &config, nil
}

func readInputFiles(paths []string) (string, error) {
  var combined []string
  for _, path := range paths {
    var content string
    
    if path == "-" {
      bytes, err := io.ReadAll(os.Stdin)
      if err != nil {
        return "", err
      }
      content = string(bytes)
    } else {
      bytes, err := os.ReadFile(path)
      if err != nil {
        return "", err
      }
      content = string(bytes)
    }
    combined = append(combined, content)
  }
  return strings.Join(combined, "\n"), nil
}

func writeYAML(path string, data interface{}) error {
  f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
  if err != nil {
    return err
  }
  defer f.Close()

  if _, err := f.WriteString("---\n"); err != nil {
    return err
  }

  return yaml.NewEncoder(f).Encode(data)
}

func executeCommands(cmds []string, dir string) (bool, string, error) {
  var output strings.Builder
  
  for _, cmd := range cmds {
    args := strings.Fields(cmd)
    command := exec.Command(args[0], args[1:]...)
    command.Dir = dir
    
    out, err := command.CombinedOutput()
    fmt.Fprintf(&output, "Command: %s\nRC: %d\nOutput:\n%s\n",
      cmd, command.ProcessState.ExitCode(), string(out))
    
    if err != nil {
      return false, output.String(), nil
    }
  }
  
  return true, output.String(), nil
}