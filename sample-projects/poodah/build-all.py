from datetime import datetime
import subprocess
import argparse

def run_command(command):
    rc = subprocess.run(command, shell=True, check=True)

def main(max_iterations=12):
    run_command("python ./riip_tools/generator.py ./project_plan.yaml")
    run_command("python ./riip_tools/generator.py ./ai-workspace/development_tasks.yaml")

    # Repeat until build_review is successful or max_iterations is reached
    for i in range(max_iterations):
        print(f"Iteration {i+1}/{max_iterations}")
        try:
            run_command("python ./riip_tools/build_review.py ./ai-workspace/build-review-tasks.yaml")
            print("Build review successful!")
            break
        except subprocess.CalledProcessError:
            print("Build review failed. Attempting to fix errors...")
            run_command("python ./riip_tools/fix_errors.py ./ai-workspace/build-review-tasks.yaml")
    else:
        print(f"Max iterations ({max_iterations}) reached without successful build review.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run build script with configurable max iterations.")
    parser.add_argument("--n", type=int, default=12, help="Maximum number of iterations (default: 12)")
    args = parser.parse_args()

    start_time = datetime.now()

    main(max_iterations=args.n)

    print(f"Time elapsed: {datetime.now() - start_time}")
