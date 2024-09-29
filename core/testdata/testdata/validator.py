import subprocess

result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
output = result.stdout.strip()

expected = '97'
if output == expected:
    exit(0)
else:
    print(f'Expected {expected}, got {output}')
    exit(1)