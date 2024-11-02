# BEGIN MAIN TASK #

Your task is to refactor and rewrite this entire codebase (requirements and code above) in Golang.

# Specific requirements for the Golang conversion:

- DO NOT modify the provided go.mod file. Use only the dependencies given.
- Put ALL of the source code into a 'cmd/gen-3' folder, and `package main`.
- Convert the integration test to its own separate _test.go file in the main package; do not add tests for edge-cases, error handling, stress tests, or negative test scenarios; only test happy path of supported usage.
- Break down the code into as many files as possible, one function per file, all structs in one file.
- Make all system prompts and user prompts configurable via named templates in a "prompt_config.yaml" file, extract this from the existing code. Assume executable and config will be in same folder.
- Remove all hard-coded constants, including prompt templates, into a yaml config file.
- Create a separate impl source file for every struct.
- Do not alter the semantics of the -l, -n, -o, and -x CLI options.

Based on the AWS API documentation, let's analyze the Python code and create a strategy for Golang conversion:

- AWS Client Setup
  - Python: `boto3.client('bedrock-runtime')` with config
  - Golang: Use `aws-sdk-go-v2/service/bedrockruntime` with context and config

- Model Constants
  - Extract String list of model identifiers to a yaml config file

- Client Configuration
  - Golang: Use `aws.Config` with custom HTTP client settings, pull settings into yaml config file.

- Base Configuration
  - add the following contents of base-prompt.json literally to a yaml config file:
  [ 
    { "role": "user", "content": "From now on, always answer without any markdown or commentary. What's 2+2?" },
    { "role": "assistant", "content": "4" }
  ]

- Message Structure
  - Python: List of dictionaries for chat history
  - Golang: Define message struct with json tags: `type Message struct`

- Error Handling
  - Python: Python exceptions
  - Golang: Go-style explicit error handling with multiple return values

- API Endpoints
  - Python: Uses bedrock-runtime endpoint
  - Golang: Configure correct endpoint based on AWS region

- Request/Response
  - Python: JSON marshaling/unmarshaling
  - Golang: Use `encoding/json` with proper struct definitions

- Authentication
  - Python: AWS credentials via boto3
  - Golang: Use AWS SDK v2 credentials provider

- Timeouts
  - Python: Connection and read timeouts
  - Golang: Context-based timeouts with `context.WithTimeout`, setup in yaml config.

- Logging
  - Python: Print to stderr
  - Golang: Use structured logging with `log` package, setup in yaml config.

Key implementation considerations:
- Use AWS SDK v2 for better context support and modern Go patterns
- Implement proper error handling with Go idioms
- Use strong typing for all API structures
- Implement context support for timeouts and cancellation
- Follow AWS service endpoint conventions for bedrock-runtime
- Support all Claude model versions as documented in the API
- Use only yaml v3

The error occurs because Bedrock requires that:
- All messages must have non-empty content except for the optional final assistant message
- The messages array cannot be empty
- The content field must be properly validated before sending to the API

The fixes include:
- Adding message content validation before making the API call
- Ensuring the user prompt is not empty
- Validating the entire message chain before sending to Bedrock
- Properly handling the response validation from Bedrock


# Contents of provided go.mod below:
