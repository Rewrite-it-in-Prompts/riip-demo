#
# gen-1.py: Single-file code generation with LLM. This can only manage one file at a time.
#

import os
import re
import sys
import subprocess
import argparse
from llm_client import CodingChat
import difflib

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate code using LLM from input files')
    parser.add_argument('input_files', nargs='+', help='Input files (use "-" for stdin)')
    parser.add_argument('-o', '--output', default="-", help='Output file path')
    parser.add_argument('-l', '--language', default="python", help='Language hint (default: python)')
    parser.add_argument('-x', '--execute', action='append', nargs='*', help='Commands to execute after generation (default: python <output>)')
    parser.add_argument('-n', '--max-retries', type=int, default=1, help='Max retries on failure')
    
    args = parser.parse_args()
    if args.execute and not args.execute[0]:
        args.execute = [f"python {args.output}"]
    elif args.execute:
        args.execute = [a[0] for a in args.execute]
    else:
        args.execute = []
    return args

def read_input_files(file_paths):
    combined_input = []
    for path in file_paths:
        if path == '-':
            combined_input.append(sys.stdin.read())
        else:
            with open(path, 'r') as file:
                combined_input.append(file.read())
    return '\n'.join(combined_input)

def generate_code(chat, input_text, args):
    system_prompt = f"""You are an expert programmer who writes clean, efficient, and well-documented code in {args.language}. Your task is to generate code for the file `{args.output}` based on the provided instructions.
    """
    retry_count = 0
    next_message = input_text

    while retry_count <= args.max_retries:
        print(f"{chat.session}: Generating code (attempt {retry_count + 1}/{args.max_retries})...", file=sys.stderr)
        generated_output, _, _, _ = chat.invoke(system_prompt=system_prompt, 
                                                user_prompt=next_message, filetype=args.language)

        # only works for single file outputs
        generated_output = re.sub(fr'```{args.language}\n(.*)\n```', r'\1', generated_output, flags=re.DOTALL)

        if args.output == '-':
            print(generated_output)
        else:
            if os.path.exists(args.output):
                with open(args.output, 'r') as file:
                    existing_content = file.read()
                diff = difflib.unified_diff(
                    existing_content.splitlines(), 
                    generated_output.splitlines(), 
                    fromfile='existing', 
                    tofile='generated', 
                    lineterm=''
                )
                print('\n'.join(diff), file=sys.stderr)
                
            with open(args.output, 'w') as file:
                file.write(generated_output)
            print(f"{chat.session}: Wrote generated code to {args.output}", file=sys.stderr)

        if args.max_retries == 0:
            return

        for command in args.execute:
            process = subprocess.run(re.split(r'(?<!\\)\s+', command),
                                        capture_output=True, text=True, input=generated_output)
            
            print(f"{chat.session}: <<[{sys.argv[0]}] executed [{command}], output: <{(process.stdout + process.stderr).strip()}>, returncode={process.returncode}>>", file=sys.stderr)

            if process.returncode != 0:
                print(f"{chat.session}: Execution of test `{command}` failed, rc={process.returncode}\n\tstdout={process.stdout}\n\tstderr={process.stderr}", file=sys.stderr)
                
                error_message = f"Execution of test `{command}` failed, got this output: {process.stdout}\n{process.stderr}"
                review_output, _, _, _ = chat.invoke (
                    system_prompt="You are an expert developer who knows how to interpret errors and extrapolate root causes. You are also aware of LLM quirkiness (such as adding unsolicited commentary) and can provide the necessary corrections.",
                    user_prompt=f"Review the following error message and provide prescriptive recommendation of what exactly needs to be fixed:\n{error_message}. Keep your fixes general and avoid hardcoding specific solutions to get around the immediate error. Do not drift from the original architecture and purpose of the {args.output} code.",
                    filetype="error_review"
                )
                next_message = f"Thanks for the review. NOW FIX THE CODE. Target file: {args.output}"
                retry_count += 1
                break  # stop running commands, fall into retry logic
        
        else:
            print(f"{chat.session}: Generated code executed successfully [{args.output}].", file=sys.stderr)
            return

    print(f"{chat.session}: Maximum retries reached. Code generation failed [{args.output}]", file=sys.stderr)
    sys.exit(1)

def main():
    args = parse_arguments()
    chat = CodingChat()

    print(f"{chat.session}: Started {sys.argv[0]} {args}", file=sys.stderr)
    input_text = read_input_files(args.input_files)

    generate_code(chat, input_text, args)

if __name__ == '__main__':
    main()