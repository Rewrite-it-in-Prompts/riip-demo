import os
import re
import sys
import yaml
import subprocess
import argparse
from llm_client import CodingChat
from pathlib import Path

def parse_arguments():
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(description='Generate multi-file code using LLM')
    parser.add_argument('input_files', nargs='+', help='Input files (use "-" for stdin)')
    parser.add_argument('-o', '--output', required=True, help='Output directory path')
    parser.add_argument('-l', '--language', default="python", help='Primary language hint')
    parser.add_argument('-x', '--execute', action='append', nargs='*', help='Commands to execute after generation')
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
    """Combine content from multiple input files."""
    combined_input = []
    for path in file_paths:
        if path == '-':
            combined_input.append(sys.stdin.read())
        else:
            with open(path, 'r') as file:
                combined_input.append(file.read())
    return '\n'.join(combined_input)

def scan_output_dir(output_dir, target_extensions):
    """Recursively scan output directory for existing files."""
    excluded_dirs = {'target', 'debug', 'node_modules'}
    files_dict = {}
    
    for root, dirs, files in os.walk(output_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in target_extensions):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)
                with open(full_path, 'r') as f:
                    files_dict[rel_path] = f.read()
    
    return files_dict

def get_architecture(chat, input_text, output_dir, max_retries):
    """Generate or load architecture specification."""
    arch_path = os.path.join(output_dir, 'architecture.yaml')
    
    if os.path.exists(arch_path):
        print(f"{chat.session}: Found existing architecture.yaml", file=sys.stderr)
        with open(arch_path, 'r') as f:
            arch = yaml.safe_load(f)
            
        target_exts = {os.path.splitext(f['path'])[1] for f in arch['filelist']}
        existing_files = scan_output_dir(output_dir, target_exts)
        
        if existing_files:
            return resume_architecture(chat, input_text, arch, existing_files, max_retries)
        return arch
    
    return generate_architecture(chat, input_text, max_retries)

def generate_architecture(chat, input_text, max_retries):
    """Generate initial architecture specification."""
    system_prompt = """Generate architecture.yaml in this format:
vision: |
  <detailed requirements>
filelist:
  - path: file1.py
    description: purpose
    content: optional_content
"""
    
    for attempt in range(max_retries + 1):
        print(f"{chat.session}: Generating architecture (attempt {attempt + 1})", file=sys.stderr)
        response, _, _, _ = chat.invoke(system_prompt=system_prompt, user_prompt=input_text,
                                      filetype="yaml")
        
        try:
            return yaml.safe_load(response)
        except yaml.YAMLError as e:
            if attempt == max_retries:
                raise e
            print(f"{chat.session}: YAML parsing failed, retrying...", file=sys.stderr)

def resume_architecture(chat, input_text, arch, existing_files, max_retries):
    """Resume from existing architecture with potential updates."""
    prompt = f"""
{input_text}
---
Architecture: {yaml.dump(arch)}
Existing files: {yaml.dump(existing_files)}
Review and respond in YAML:
vision: |
  <updated vision>
filelist: [] or updated list
"""
    
    for attempt in range(max_retries + 1):
        print(f"{chat.session}: Reviewing architecture (attempt {attempt + 1})", file=sys.stderr)
        response, _, _, _ = chat.invoke(system_prompt="Review and update architecture", 
                                      user_prompt=prompt,
                                      filetype="yaml")
        
        try:
            update = yaml.safe_load(response)
            if update['filelist']:
                arch['filelist'] = update['filelist']
            arch['vision'] = update['vision']
            return arch
        except yaml.YAMLError as e:
            if attempt == max_retries:
                raise e
            print(f"{chat.session}: YAML parsing failed, retrying...", file=sys.stderr)

def generate_file(chat, file_spec, arch, output_dir, language):
    """Generate content for a single file."""
    if 'content' in file_spec:
        return file_spec['content']
        
    prompt = f"""Generate {file_spec['path']} based on:
Architecture: {yaml.dump(arch)}
File description: {file_spec['description']}"""
    
    response, _, _, _ = chat.invoke(system_prompt=f"Generate {file_spec['path']}", 
                                  user_prompt=prompt,
                                  filetype=language)
    return response

def handle_error(chat, error_info, arch, max_retries):
    """Handle errors during generation or execution."""
    prompt = f"""Analyse error and respond in YAML:
root-cause: <analysis>
immediate-fix: <specific fix>
best-practice: <guidance>
filelist:
  - path: file1.py
    description: purpose
    content: content

Error: {error_info}
Current architecture: {yaml.dump(arch)}"""
    
    for attempt in range(max_retries + 1):
        print(f"{chat.session}: Analyzing error (attempt {attempt + 1})", file=sys.stderr)
        response, _, _, _ = chat.invoke(system_prompt="Analyze error", 
                                      user_prompt=prompt,
                                      filetype="yaml")
        
        try:
            fix = yaml.safe_load(response)
            return fix
        except yaml.YAMLError as e:
            if attempt == max_retries:
                raise e
            print(f"{chat.session}: YAML parsing failed, retrying...", file=sys.stderr)

def execute_commands(chat, commands, output_dir):
    """Execute specified commands in output directory."""
    last_stdout = ""
    last_stderr = ""
    
    for cmd in commands:
        print(f"{chat.session}: Executing: {cmd}", file=sys.stderr)
        process = subprocess.run(re.split(r'(?<!\\)\s+', cmd),
                               capture_output=True, text=True,
                               cwd=output_dir)
        
        last_stdout = process.stdout
        last_stderr = process.stderr
        print(f"{chat.session}: Command output: {last_stdout}{last_stderr}", 
              file=sys.stderr)
        
        if process.returncode != 0:
            return False, f"Command '{cmd}' failed: {last_stderr}", last_stdout, last_stderr
    return True, None, last_stdout, last_stderr

def main():
    """Main entry point for multi-file code generation."""
    args = parse_arguments()
    chat = CodingChat()
    os.makedirs(args.output, exist_ok=True)
    
    print(f"{chat.session}: Started multi-file generation", file=sys.stderr)
    input_text = read_input_files(args.input_files)
    
    try:
        arch = get_architecture(chat, input_text, args.output, args.max_retries)
        
        for file_spec in arch['filelist']:
            file_path = os.path.join(args.output, file_spec['path'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            print(f"{chat.session}: Generating {file_spec['path']}", file=sys.stderr)
            content = generate_file(chat, file_spec, arch, args.output, args.language)
            
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"{chat.session}: Wrote {file_spec['path']}", file=sys.stderr)
        
        if args.execute:
            success, error, stdout, stderr = execute_commands(chat, args.execute, args.output)
            if not success:
                fix = handle_error(chat, f"Error: {error}\nStdout: {stdout}\nStderr: {stderr}", 
                                 arch, args.max_retries)
                with open(os.path.join(args.output, 'implementation.yaml'), 'a') as f:
                    f.write('---\n' + yaml.dump(fix))
                
                if fix['filelist']:
                    for file_spec in fix['filelist']:
                        file_path = os.path.join(args.output, file_spec['path'])
                        content = generate_file(chat, file_spec, arch, args.output, args.language)
                        with open(file_path, 'w') as f:
                            f.write(content)
            else:
                print(stdout, end='')
    
    except Exception as e:
        print(f"{chat.session}: Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()