import re
import sys
import yaml
import os
import subprocess
from lib.llm_client import invoke_model
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

MAX_ITERATIONS = 6

@dataclass
class ValidationResult:
    success: bool
    stdout: str
    stderr: str

class CodeGenerator:
    def __init__(self, config: dict, strategies: dict, workspace: str):
        self.config = config
        self.strategies = strategies
        self.workspace = workspace
        self.failed_validations = 0
        self.all_targets = self._collect_all_targets()
    
    def _collect_all_targets(self) -> Set[str]:
        """Collect all target files specified in the configuration."""
        targets = set()
        for task in self.config['tasks']:
            if 'target' in task:
                targets.add(task['target'])
            if 'targets' in task:
                targets.update(task['targets'])
        return targets

    def write_file(self, filename: str, content: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def read_file(self, filename: str) -> str:
        """Read content from a file"""
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def get_task_for_target(self, target: str) -> Optional[dict]:
        """Find the task that contains this target"""
        return next((task for task in self.config['tasks'] 
                    if task.get('target') == target 
                    or target in task.get('targets', [])), None)

    def get_related_files(self, target: str) -> List[str]:
        """Get all files generated from the same task as the target"""
        task = self.get_task_for_target(target)
        if not task:
            return []
        
        # For single target tasks
        if 'target' in task:
            return [task['target']]
            
        # For multi-target tasks
        return task.get('targets', [])

    def reconstruct_prompt(self, target: str) -> str:
        """Reconstruct the complete prompt including vision, task prompt, imports, and related files"""
        # Start with vision
        base_prompt = self.config['vision']
        
        # Find the task for this target
        task = self.get_task_for_target(target)
        if not task:
            return base_prompt
            
        # Add task prompt
        base_prompt += task['prompt']
        
        # Add imports
        for import_path in task.get('imports', []):
            if import_path.startswith("lib:"):
                import_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), import_path[4:])
            else:
                import_path = os.path.join(self.workspace, import_path)
            
            content = self.read_file(import_path)
            base_prompt += f"\nFile attached for your reference:\n<context file='{import_path}'>\n{content}\n</context>\n"
            
        # Add related files from the same task
        for related_file in self.get_related_files(target):
            if related_file != target:  # Don't include the current target
                file_path = os.path.join(self.workspace, related_file)
                if os.path.exists(file_path):
                    content = self.read_file(file_path)
                    base_prompt += f"\n\nFor reference, here's the already generated {related_file}:\n"
                    base_prompt += f"<context file='{related_file}'>\n{content}\n</context>\n"
                
        return base_prompt

    def generate_content(self, prompt: str, content_type: str, system: str, filename: Optional[str] = None) -> str:
        if filename:
            prompt_file = os.path.join(self.workspace, f".prompts/{filename}.prompt")
            os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
            self.write_file(prompt_file, prompt)
            
        print(f"Generating: {filename or content_type}", file=sys.stderr)

        output, in_tokens, out_tokens = invoke_model(prompt, system, filename or "output.txt")
        print(f"Generated {content_type}: {in_tokens} in tokens, {out_tokens} out tokens.", file=sys.stderr)
        
        if filename:
            full_path = os.path.join(self.workspace, filename)
            self.write_file(full_path, output)
        return output

    def get_test_targets(self) -> List[Tuple[str, str]]:
        """Get the test target patterns from strategies"""
        return self.strategies['globals']['test_targets']

    def get_test_target(self, filename: str) -> Optional[str]:
        """Determine test target filename based on test target patterns"""
        for pattern, replacement in self.get_test_targets():
            if re.search(pattern, filename):
                return re.sub(pattern, replacement, filename)
        return None

    def run_build_and_test(self) -> List[ValidationResult]:
        """Run build and test steps for the project and return results"""
        results = []
        project_config = self.strategies['project-types'][self.config['project-type']]
        
        # Run build step
        for build_step in project_config['build']:
            print(f"\nRunning build step: {build_step}", file=sys.stderr)
            build_result = subprocess.run(build_step, 
                                        capture_output=True, text=True,
                                        cwd=self.workspace)

            print(f"Build result: {build_result.returncode}, \nSTDOUT:\n{build_result.stdout}\nSTDERR:\n{build_result.stderr}", file=sys.stderr)

            if build_result.returncode != 0:
                results.append(ValidationResult(False, build_result.stdout, build_result.stderr))
                break
        else:  # Only run test if all build steps succeeded
            # Run test step
            print(f"\nRunning test step: {project_config['test']}", file=sys.stderr)
            test_result = subprocess.run(project_config['test'].split(' '), 
                                    capture_output=True, text=True, cwd=self.workspace)
            results.append(ValidationResult(
                test_result.returncode == 0,
                test_result.stdout,
                test_result.stderr
            ))

            print(f"Test result: {test_result.returncode}, \nSTDOUT:\n{test_result.stdout}\nSTDERR:\n{test_result.stderr}", file=sys.stderr)
        
        return results

    def collect_target_files_content(self) -> List[str]:
        """Collect content only from files that were specified as targets in the config"""
        files_content = []
        for target in self.all_targets:
            file_path = os.path.join(self.workspace, target)
            if os.path.isfile(file_path):
                content = self.read_file(file_path)
                files_content.append(f"<file path='{target}'>\n{content}\n</file>\n")
        return files_content

    def initial_generation(self, tasks: List[dict]) -> None:
        """First pass: Generate all implementation and test files"""
        project_config = self.strategies['project-types'][self.config['project-type']].get('project-config-file')
        if project_config:
            for file_config in project_config:
                if 'lock' in file_config:
                    if not os.path.exists(os.path.join(self.workspace, file_config['target'])):
                        self.write_file(os.path.join(self.workspace, file_config['target']), file_config['content'])
                else:
                    self.write_file(os.path.join(self.workspace, file_config['target']), file_config['content'])

        for task in tasks:
            if 'content' in task:
                self.write_file(os.path.join(self.workspace, task['target']), task['content'])
                continue

            # Handle both single target and multiple targets
            targets = task.get('targets', [task['target']] if 'target' in task else [])
            
            # Generate each target in sequence
            for target in targets:
                target_path = os.path.join(self.workspace, target)
                if os.path.isfile(target_path):
                    print(f"{target} Script already exists. Skipping generation.", file=sys.stderr)
                    continue

                # Build working prompt for this target using reconstruct_prompt
                working_prompt = self.reconstruct_prompt(target)
                working_prompt += f"\n\nYour task now is to write the file {target}."

                # Generate implementation
                test_targets = self.get_test_targets()
                self.generate_content(working_prompt, "code", self.strategies['project-types'][self.config['project-type']]['role'], target)

                # Generate test file if we have test target patterns
                if test_targets:
                    test_target = self.get_test_target(target)
                    if test_target:
                        implementation = self.read_file(target_path)
                        test_prompt = self.strategies['globals']['testing_template'].format(
                            target=target,
                            output=implementation,
                            test_target=test_target,
                            prompt=working_prompt
                        )
                        self.generate_content(test_prompt, "test", self.strategies['project-types'][self.config['project-type']]['role'], test_target)
                        
    def validate_and_refine(self) -> None:
        """Validate and refine all generated files"""
        iteration_number = MAX_ITERATIONS
        
        while iteration_number > 0:
            iteration_number -= 1
            print(f"\nValidation attempt {MAX_ITERATIONS - iteration_number}", file=sys.stderr)
            
            # Run build and test
            validation_results = self.run_build_and_test()
            
            # If validation passed, we're done
            if all(result.success for result in validation_results):
                print("\n*** All validations passed successfully!", file=sys.stderr)
                return
            
            # Collect all target files content
            all_files_content = self.collect_target_files_content()
            
            review_output = self.generate_content(
                self.strategies['globals']['review_template'].format(
                    prompt=self.config['vision'],
                    output='\n'.join(all_files_content),
                    error_output=f"STDOUT:\n{validation_results[0].stdout}\nSTDERR:\n{validation_results[0].stderr}"
                ),
                content_type="review",
                system="You are an expert technical reviewer, troubleshooter, and root cause analyst."
            )

            try:
                file_fixes = yaml.safe_load(review_output)
                if not isinstance(file_fixes, dict):
                    raise ValueError("Review must be a dictionary of file paths to fixes")
            except:
                print(f"*** Failed to parse review output as YAML:\n{review_output}", file=sys.stderr)
                sys.exit(1)

            # Apply fixes to specific files
            for file_path, fix in file_fixes.items():
                full_path = os.path.join(self.workspace, file_path)
                if not os.path.exists(full_path):
                    print(f"Warning: Review specified fixes for non-existent file {file_path}", file=sys.stderr)
                    continue
                    
                print(f"\nApplying fixes to {file_path}", file=sys.stderr)
                print(f"Fix:\n{fix}", file=sys.stderr)
                
                # Get current content from filesystem
                current_content = self.read_file(full_path)
                
                # Use the complete prompt for fixing
                target = self.get_test_target(file_path)  # Derive original file using test_targets
                if not target:
                    target = file_path  # Fallback to the file itself if no match found
                
                task = self.get_task_for_target(target)
                
                if task and 'lock' in task:
                    print(f"Refusing to modify locked file {file_path}", file=sys.stderr)
                    continue

                full_prompt = self.reconstruct_prompt(target)
                fixing_prompt = self.config['globals']['fixing_template'].format(
                    prompt=full_prompt,
                    output=current_content,
                    error_output=f"STDOUT:\n{validation_results[0].stdout}\nSTDERR:\n{validation_results[0].stderr}",
                    review=fix,
                    target=file_path
                )

                # Generate and write the fixed content
                self.generate_content(fixing_prompt, 
                                      content_type="fixed file", 
                                      system=self.config['project-types'][self.config['project-type']]['role'], 
                                      filename=file_path)
        
        self.failed_validations = sum(1 for result in validation_results if not result.success)
        print(f"\n*** Failed to validate after {MAX_ITERATIONS - iteration_number} attempts.", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <config_file>")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    strategies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "riip-strategies.yaml")
    with open(strategies_path, "r") as f:
        strategies = yaml.safe_load(f)
        
    workspace = os.path.join(os.path.dirname(os.path.abspath(config_path)), config.get('workspace', '.'))
    os.makedirs(workspace, exist_ok=True)
    
    generator = CodeGenerator(config, strategies, workspace)
    generator.initial_generation(config['tasks'])
    generator.validate_and_refine()
    
    if generator.failed_validations > 0:
        print(f"Failed validations: {generator.failed_validations}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()