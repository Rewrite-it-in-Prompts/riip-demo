import os
import platform
import subprocess

build_dir = os.path.dirname(os.path.abspath(__file__))

os.makedirs(f"{build_dir}/project/src", exist_ok=True)

build_command = [
    "docker", "build",
    "-t", "gen-3-rs", 
    "-f", f"{build_dir}/Dockerfile",
    "."
]

print("Building Docker image...")
subprocess.run(build_command, check=True)

# Get the user's home directory for AWS credentials
if platform.system() == "Windows":
    aws_path = os.path.join(os.environ['USERPROFILE'], '.aws')
else:
    aws_path = os.path.join(os.path.expanduser('~'), '.aws')

# Run the Docker container
run_command = [
    "docker", "run",
    "-v", f"{aws_path}:/root/.aws",
    "-v", f"{os.path.abspath(f'{build_dir}/project')}:/build/project",
    "-it", "gen-3-rs"
]

print("Running Docker container...")
subprocess.run(run_command, check=True)
