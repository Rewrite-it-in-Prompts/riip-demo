#
# "Gen-1" Code generator using LLM to produce single-file programs, with iterative
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
    parser.add_argument('-o', '--output', default=".generated.py", help='Output file path')
    parser.add_argument('-x', '--executor', default=None, help='Interpreter to execute generated code and iterate on errors')
    parser.add_argument('-n', '--max-retries', type=int, default=3, help='Maximum number of retries on execution failure (default: 3)')
    return parser.parse_args()


def read_input_files(file_paths):
    combined_input = []

    for path in file_paths:
        if path == '-':
            combined_input.append(sys.stdin.read())
        else:
            with open(path, 'r') as file:
                combined_input.append(file.read())

    return '\n'.join(combined_input)


def execute_code(code, executor, output_file):
    if '--' in executor:
        cwd, filename = os.path.split(output_file)
        cmd = executor.replace('--', filename).split()
    else:
        cmd = executor.split()
        cwd = '.'

    print(f"Executing generated code... cwd={cwd}, cmd={cmd}\n", file=sys.stderr)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    std_out, std_err = process.communicate()

    print(f"Execution output (stdout):\n{std_out}", file=sys.stderr)
    print(f"Execution output (stderr):\n{std_err}", file=sys.stderr)

    return process.returncode, std_out, std_err


def review_error(chat, error_message):
    review_output, ni, no, _ = chat.invoke(
        system_prompt="You are an expert Build Coordinator and DevOps Pipeline Operator who knows how to interpret build errors and how to tell developers to fix their code so that they get it right next time. You do not write the code for them, but you provide prescriptive advice highlighting the specific mistakes they have made, and how to fix it. Your reviews are so thorough that some developers may think you are being condescending, but you're really just being detailed.",
        user_prompt=f"Review the following build errors in context of the entire chat history: {error_message}.",
        filetype="Build Failure Review")
    print(f"======\nReview output:\n{review_output}\n======\n", file=sys.stderr)

    next_message = "\nOk great. Now provide the actual fixes. Provide the fixed code in full. The human has difficulty typing, so do not leave placeholders or copy-paste instructions."
    return next_message


def generate_code(chat, input_text, output_file, executor, max_retries):
    retry_count = 0
    next_message = input_text

    while next_message:
        print(f"\n*** Attempt {retry_count + 1} ...", file=sys.stderr)

        if os.path.exists(output_file):
            os.remove(output_file)

        extension = os.path.splitext(output_file)[1]
        generated_code, ni, no, chat_state = chat.invoke(next_message, extension)

        with open(output_file, 'w') as file:
            file.write(generated_code)

        print(f"Generated code saved to {output_file}", file=sys.stderr)

        if 'TODO' in generated_code:
            next_message = "The generated code contains placeholders (TODO). Please generate the complete code."
        elif executor:
            return_code, std_out, std_err = execute_code(generated_code, executor, output_file)
            if return_code == 0:
                print(f"SUCCESS! Generated code saved to {output_file}", file=sys.stderr)
                return
            else:
                retry_count += 1
                print(f"Retry {retry_count}/{max_retries}...", file=sys.stderr)
                error_message = f"Process failed with exit code {return_code}\n\nStandard output:\n{std_out}\n\nError output:\n{std_err}\n"
                print(f"Error executing code: {error_message}", file=sys.stderr)
                next_message = review_error(chat, error_message)
        else:
            return

        if retry_count >= max_retries:
            print(f"\n*** Maximum retries ({max_retries}) reached ***", file=sys.stderr)
            sys.exit(1)


def main():
    args = parse_arguments()
    input_text = read_input_files(args.input_files)

    chat = CodingChat()
    generate_code(chat, input_text, args.output, args.executor, args.max_retries)


if __name__ == '__main__':
    main()