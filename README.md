# RIIP: Rewrite it in Prompts

Utilities for Continuous Generation of source code from prompts.

RIIP is organized as a series of progressively more complex code generation utilities:

Gen-1:

    Basic code generator which can produce a single-source-file Python program reliably.
    The gen-1 code was human-written, and is solely focused on Python.
    Gen-1 can be executed directly in the command-line environment with these steps:

      - Install Python
      - Configure your AWS credentials
      - Enable Bedrock in the AWS Console
      - Execute in command line:

            pip install boto3
            # quick test:
            cd core
            echo "Print all primes from 1 to 100" | python gen-1.py -x -

Gen-2:

    Improved code generator that can produce multi-file projects.
    The code for the gen-2 generator is maintained by the gen-1 generator, with this command:

      pip install pyyaml
      python gen-1.py gen-1.py gen-2-specs.txt -o gen-2.py -x

    The gen-2 generator takes a "validator" parameter, which paves the way for generating
    multi-file projects in languages such as Java, Golang, Rust, etc.

    Gen-2 is driven by a YAML file, which is more suitable for batch processing than gen-1's CLI.

Gen-3:

    The gen-3 generator is a full rewrite of the Gen-2 generator in Java, Golang, and Rust, 
    optimized for generating complex projects in each of those languages.

    This is capable of creating larger multi-file projects, on the scale of a typical microservice.

    Rewriting the generator to match its target language is convenient for the human using it,
    for instance, by removing the need to manage Python installation in a Java build environment.

    The code for the gen-3 generator(s) is maintained by the gen-2 generator, with this command:

      python gen-2.py gen-3-specs.yaml

Gen-4:

    Not built yet. It is envisioned this would be able to generate distributed system architectures
    with multiple complex components, or very large modular monolithic applications.
