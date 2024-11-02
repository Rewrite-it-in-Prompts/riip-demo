# RIIP: Rewrite it in Prompts

Utilities for Continuous Generation of source code from prompts.

This repo was originally created as a companion to my LinkedIn Article: "Throw away the source code: Reimagining Software Development with GenAI" - https://www.linkedin.com/pulse/throw-away-source-code-reimagining-software-genai-alex-ramos-khedc

Original code from the LinkedIn article is found under `sample-projects\poodah`. I have refactored a bit since then, and it is now organized as a series of progressively more complex code generation utilities named `gen-1`, `gen-2`, and `gen-3`:

# Gen-1

Basic code generator written in Python. The gen-1 code is human-written and human-maintained, 
so it should be kept very minimal. Gen-1 is executed directly in the command-line environment
with these steps:

  - Install Python
  - Configure your AWS credentials
  - Enable Bedrock in the AWS Console
  - Execute in command line:

        pip install boto3 pyyaml
        # quick test:
        cd core
        echo "Print all primes from 1 to 100" | python gen-1.py - -x "python -"

# Gen-2

Improved code generator that can produce projects spanning multiple source and config files.
The code for the gen-2 generator is maintained by the gen-1 generator.

A Makefile is included in the project:
- To regenerate the code, use `make gen-2.py`, or `python -mpymake gen-2.py`

# Gen-3

Refactored and more configurable implementation of the gen-2 generator.

The `gen-3` folder contains a collection of rewrites of `gen-2.py` in a few different languages. Each of these rewrites is currently in different stages of experimentation:

## Go

This is the most complete. `make g3-golang`

## Rust

Investigation in progress.

## Java

Investigation in progress.

## Typescript

Investigation in progress.
