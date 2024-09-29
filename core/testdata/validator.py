
import subprocess
import sys
import os

def validate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(script_dir, 'main.py')
    
    result = subprocess.run(
        [sys.executable, main_path],
        capture_output=True,
        text=True
    )
    
    output = result.stdout.strip()
    expected = '97'
    
    if output != expected:
        print(f'Expected {expected}, got {output}')
        return False
    return True

if __name__ == '__main__':
    if not validate():
        sys.exit(1)
