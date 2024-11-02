package main

import (
    "context"
    "fmt"
    "os"
    "path/filepath"
)

type Generator struct {
    chat   *CodingChat
    args   *Args
}

func NewGenerator(chat *CodingChat, args *Args) *Generator {
    return &Generator{
        chat: chat,
        args: args,
    }
}

func (g *Generator) Generate(input string) error {
    ctx := context.Background()
    
    archPath := filepath.Join(g.args.outputDir, "architecture.yaml")
    implPath := filepath.Join(g.args.outputDir, "implementation.yaml")

    var arch Architecture
    if _, err := os.Stat(archPath); err == nil {
        arch, err = g.resumeProject(ctx, archPath, input, "")
        if err != nil {
            return err
        }
    } else {
        arch, err = g.getArchitecture(ctx, input)
        if err != nil {
            return err
        }
        if err := writeYAML(archPath, arch); err != nil {
            return err
        }
    }

    retryCount := 0
    for retryCount <= g.args.maxRetries {
        if err := g.processArchitecture(ctx, arch); err != nil {
            return err
        }

        if len(g.args.execute) == 0 {
            return nil
        }

        success, output, err := executeCommands(g.args.execute, g.args.outputDir)
        if err != nil {
            return err
        }

        if success {
            fmt.Println(output)
            return nil
        }

        fixes, err := g.fixErrors(ctx, output)
        if err != nil {
            return err
        }

        if err := writeYAML(implPath, fixes); err != nil {
            return err
        }

        arch.FileList = fixes.FileList
        retryCount++
    }

    return fmt.Errorf("max retries exceeded")
}