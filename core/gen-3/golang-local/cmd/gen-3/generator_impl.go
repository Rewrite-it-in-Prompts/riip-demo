package main

import (
  "context"
  "fmt"
  "os"
  "path/filepath"
  
  "gopkg.in/yaml.v3"
)

func (g *Generator) getArchitecture(ctx context.Context, input string) (Architecture, error) {
  prompt := fmt.Sprintf(g.chat.config.Templates.UserPrompts["architecture"], input)
  
  content, err := g.chat.Invoke(ctx, prompt, "yaml", "")
  if err != nil {
    return Architecture{}, err
  }

  var arch Architecture
  if err := yaml.Unmarshal([]byte(content), &arch); err != nil {
    return Architecture{}, err
  }

  return arch, nil
}

func (g *Generator) resumeProject(ctx context.Context, archPath, input, lastOutput string) (Architecture, error) {
  arch, err := readArchitecture(archPath)
  if err != nil {
    return Architecture{}, err
  }

  targetExts := make(map[string]bool)
  for _, f := range arch.FileList {
    targetExts[filepath.Ext(f.Path)] = true
  }

  files := make(map[string]string)
  entries, err := os.ReadDir(g.args.outputDir)
  if err != nil {
    return Architecture{}, err
  }

  for _, entry := range entries {
    if !entry.IsDir() && targetExts[filepath.Ext(entry.Name())] {
      content, err := os.ReadFile(filepath.Join(g.args.outputDir, entry.Name()))
      if err != nil {
        return Architecture{}, err
      }
      files[entry.Name()] = string(content)
    }
  }

  prompt := fmt.Sprintf(
    "Review this project state:\nInput: %s\nCurrent architecture: %+v\nFiles generated: %v\nLast execution output: %s",
    input, arch, files, lastOutput)

  content, err := g.chat.Invoke(ctx, prompt, "yaml", "")
  if err != nil {
    return Architecture{}, err
  }

  var newArch Architecture
  if err := yaml.Unmarshal([]byte(content), &newArch); err != nil {
    return Architecture{}, err
  }

  return newArch, nil
}

func (g *Generator) processArchitecture(ctx context.Context, arch Architecture) error {
  if err := os.MkdirAll(g.args.outputDir, 0755); err != nil {
    return err
  }

  for _, file := range arch.FileList {
    content := file.Content
    if content == "" {
      var err error
      content, err = g.generateFile(ctx, file, arch.Vision)
      if err != nil {
        return err
      }
    }

    path := filepath.Join(g.args.outputDir, file.Path)
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
      return err
    }

    if err := os.WriteFile(path, []byte(content), 0644); err != nil {
      return err
    }
  }

  return nil
}

func (g *Generator) generateFile(ctx context.Context, file FileInfo, vision string) (string, error) {
  prompt := fmt.Sprintf(g.chat.config.Templates.UserPrompts["file_gen"],
    file.Path, file.Description, vision)
  
  return g.chat.Invoke(ctx, prompt, filepath.Ext(file.Path)[1:], "")
}

func (g *Generator) fixErrors(ctx context.Context, errorOutput string) (Implementation, error) {
  prompt := fmt.Sprintf(g.chat.config.Templates.UserPrompts["error_fix"], errorOutput)
  
  content, err := g.chat.Invoke(ctx, prompt, "yaml", "")
  if err != nil {
    return Implementation{}, err
  }

  var impl Implementation
  if err := yaml.Unmarshal([]byte(content), &impl); err != nil {
    return Implementation{}, err
  }

  return impl, nil
}

func readArchitecture(path string) (Architecture, error) {
  f, err := os.Open(path)
  if err != nil {
    return Architecture{}, err
  }
  defer f.Close()

  var arch Architecture
  if err := yaml.NewDecoder(f).Decode(&arch); err != nil {
    return Architecture{}, err
  }
  return arch, nil
}