package main

import (
    "flag"
    "os"
    "strings"
)

type Args struct {
    inputFiles  []string
    outputDir   string
    language    string
    execute     []string
    maxRetries  int
    configPath  string
}

func parseArgs() *Args {
    outputDir := flag.String("o", "", "Output directory path")
    language := flag.String("l", "python", "Primary language hint")
    maxRetries := flag.Int("n", 1, "Max retries on failure")
    configPath := flag.String("c", "prompt_config.yaml", "Path to config file")
    
    var execCmds string
    flag.StringVar(&execCmds, "x", "", "Commands to execute after generation (comma-separated)")

    flag.Parse()

    if *outputDir == "" {
        flag.Usage()
        os.Exit(1)
    }

    var execute []string
    if execCmds != "" {
        execute = strings.Split(execCmds, ",")
    }

    return &Args{
        inputFiles: flag.Args(),
        outputDir: *outputDir,
        language: *language,
        execute: execute,
        maxRetries: *maxRetries,
        configPath: *configPath,
    }
}
