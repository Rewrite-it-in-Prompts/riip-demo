# RIIP: Rewrite it in Prompts

Utilities for Continuous Generation of source code from prompts.

This repo was originally created as a companion to my LinkedIn Article: "Throw away the source code: Reimagining Software Development with GenAI" - https://www.linkedin.com/pulse/throw-away-source-code-reimagining-software-genai-alex-ramos-khedc

It has since morphed and grown a bit with a few more experiments.

Original code from the LinkedIn article is found under `sample-projects\poodah`.

RIIP is now organized as a series of progressively more complex code generation utilities:

# Gen-1

Basic code generator which can produce a single-source-file program reliably.
The gen-1 code is human-written and human-maintained, so we try to keep it very minimal.
Gen-1 is executed directly in the command-line environment with these steps:

  - Install Python
  - Configure your AWS credentials
  - Enable Bedrock in the AWS Console
  - Execute in command line:

        pip install boto3
        # quick test:
        cd core
        echo "Print all primes from 1 to 100" | python gen-1.py - -x python --

  The following works if a go.mod file is present in the same directory:

    echo "Print all primes from 1 to 100, in Go" | python gen-1.py -o primes.go - -x "go run"

# Gen-2

Improved code generator that can produce projects spanning multiple source and config files.
The code for the gen-2 generator is maintained by the gen-1 generator, with this command:

  ```PowerShell
  python gen-1.py llm_client.py gen-1.py gen-2-specs.txt targets/golang-local/guidance.txt -o targets/golang-local/gen-2.go -x "go run -- -t" -n 5
  ```

It can also be generated in Rust (currently fails testing):
  ```PowerShell
  cd core
  docker build -t gen-2-rs -f targets/rust-container/Dockerfile .
  docker run -v $Env:USERPROFILE/.aws:/root/.aws -it gen-2-rs
  ```

Experimental versions in Java and Typescript have also been started. Rewriting the generator to match its target language is convenient for the human using it, for instance, by removing the need to manage Python installation in a Java build environment.

# Gen-4

Not built yet. It is envisioned this would be able to generate distributed system architectures
with multiple complex components, or very large modular monolithic applications. This would likely
follow a more formal agentic process, a departure from the ad-hoc experimental roots of RIIP.
