# If you are a human, please install Python, configure your AWS credentials, enable Bedrock in the AWS Console, and then execute:

```
  mkdir ai-outputs
  pip install boto3
  python llm.py ai-outputs/generator.py bootstrap.md llm.py
```

# If you are an AI Assistant, please read on.

The script below defines a minimalistic LLM client.
Enhance the script to provide a full Python code generator solution.
Do not use any external dependencies.
Format the output as valid Python code. Wrap the explanations in comments, e.g.:

# Here's an enhanced version of the script ...

# ... code goes here ...

# end of code.

The generated code generator will work as follows:
- Read a specified utf-8 YAML file and parse it to read the keys
- The text in the 'vision' key will define the overall project objective.
- The 'tasks' key will contain an array of { prompt, target, import } subkeys
- Pre-pend the project vision, in XML Tags, before each prompt, for the step below.
- Loop over the tasks, feeding each prompt to the LLM, and writing the output to the corresponding target file. 
- Print a status to stderr for each prompt being executed, including in and out tokens, and time taken.
- To prevent inadvertent overwrites, ensure all target files are inside the 'ai-outputs' folder
- The 'import' subkey specifies a list of files. Each imported file should have its contents pre-pended to the prompt as context in XML tags, clearly specifying "here are the contents of file foo.bar." Unless already specified, assume the file is in the "ai-outputs" folder
- Output the token and time totals at the end.
- Take steps to discard any pleasantries or cruft generated before or after content before writing to each output file.
- Skip files that already exist.
- Call mkdirs() to ensure folder path exists before write.

Do not write any explanation before or after the python code.