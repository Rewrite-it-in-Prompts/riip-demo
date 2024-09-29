#
# "Gen-1" Code generator using LLM to produce single-file Python scripts, with iterative
# improvement based on execution results.
#
# Usage:
#   gen-1.py [-x] -o OUTPUT_FILE [INPUT_FILES...] [-n MAX_RETRIES]
#   Use "-" for stdin as input
#   '-x' flag to execute the generated code and use any errors for iterative improvement
#   '-o' specifies the output file
#   '-n' specifies maximum number of retries (default: 3)
#

import os
import sys
import subprocess
import argparse

from llm_client import CodingChat

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate code using LLM from input files')
    parser.add_argument('input_files', nargs='+', help='Input files (use "-" for stdin)')
    parser.add_argument('-o', '--output', default="generated_script.py", help='Output file path')
    parser.add_argument('-x', '--execute', action='store_true', help='Execute generated code and iterate on errors')
    parser.add_argument('-n', '--max-retries', type=int, default=3, help='Maximum number of retries on execution failure (default: 5)')
    return parser.parse_args()

def read_input_files(file_paths):
    combined_input = []
    
    for path in file_paths:
        if path == '-':
            # Read from stdin
            combined_input.append(sys.stdin.read())
        else:
            with open(path, 'r') as file:
                combined_input.append(file.read())
    
    return '\n'.join(combined_input)

def main():
    args = parse_arguments()
    
    # Read input from all specified sources
    input_text = read_input_files(args.input_files)
    next_message = input_text
    
    chat = CodingChat()
    retry_count = 0

    while True:
        print(f"\n*** Attempt {retry_count+1} ...", file=sys.stderr)

        if os.path.exists(args.output):
            os.remove(args.output)

        extension = os.path.splitext(args.output)[1]
        generated_code, ni, no, log_path = chat.invoke(next_message, extension)
        working_file = 'temp-' + args.output

        with open(working_file, 'w') as file:
            file.write(generated_code)
        
        print(f"Generated code temporarily saved to temp-{args.output}", file=sys.stderr)

        if args.execute:
            print("Executing generated code...\n", file=sys.stderr)
            
            # Execute the code using subprocess
            process = subprocess.Popen(
                [sys.executable, working_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            std_out, std_err = process.communicate()

            print(f"Execution output (stdout):\n{std_out}", file=sys.stderr)
            print(f"Execution output (stderr):\n{std_err}", file=sys.stderr)

            if process.returncode == 0:
                # Success - save the working code and exit
                os.rename(working_file, args.output)
                print(f"SUCCESS! Generated code saved to {args.output}", file=sys.stderr)
                break
            else:
                retry_count += 1
                
                print(f"Retry {retry_count}/{args.max_retries}...", file=sys.stderr)
                error_message = f"Process failed with exit code {process.returncode}\n\nStandard output:\n{std_out}\n\nError output:\n{std_err}"
                print(f"Error executing code: {error_message}", file=sys.stderr)
                next_message = f"\nThat's not working. Please evaluate carefully and provide a fix. Start with new changelog comments explaining what's going on. Here's the error:\n{error_message}\n\nProvide the fixed code in full, the human has difficulty typing."

                if retry_count >= args.max_retries:
                    print(f"\n*** Maximum retries ({args.max_retries}) reached ***", file=sys.stderr)
                    sys.exit(1)

        else:
            break

if __name__ == '__main__':
    main()