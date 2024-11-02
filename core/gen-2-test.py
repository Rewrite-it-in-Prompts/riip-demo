import os
import subprocess
import sys
import random
import uuid

target_num = random.randint(100000, 1000000)

id = str(uuid.uuid4())  # For debugging purposes

print(f"{id}: Testing gen-2.py to find the largest prime under {target_num}...")	

# Function to find the largest prime under a given number
def find_largest_prime_under(n):
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
    
    for num in range(n - 1, 1, -1):
        if is_prime(num):
            return num
    return None

# Calculate the expected largest prime for validation
expected_prime = find_largest_prime_under(target_num)

prompt = f"""Generate the largest prime number under the value specified in sys.argv[1]. Create separate source files for the calculation function in calc.py and main() in main.py, which will write the number to stdout and also echo the value of sys.argv[2]. Do not create any other files. Main will require sys.path.append(os.path.dirname(__file__)) in order to find the import."""

os.chdir(os.path.join(os.path.dirname(__file__)))

result = subprocess.run(["python", "gen-2.py", "-", 
                         "-o", "gen-2-test", "-n", "1",
                         "-x", f"python main.py {target_num} {id}"],
                    input=prompt, text=True, capture_output=True)

if result.returncode != 0:
    print(f"{id}: generation and execution of main.py via gen-2.py failed with returncode={result.returncode}. stdout=[{result.stdout.replace('\n', '\n\t')}], stderr=[{result.stderr.replace('\n', '\n\t')}]. Analyse errors in this context.")
    sys.exit(1)

if str(expected_prime) not in result.stdout:
    print(f"{id}: generation and execution of main.py via gen-2.py returned returncode=0 but does not contain the expected number. stdout=[{result.stdout.replace('\n', '\n\t')}], stderr=[{result.stderr.replace('\n', '\n\t')}]. Check if -x option is coded correctly to pass the output.")
    sys.exit(1)

else:
    print(f"{id}: PASSED test - correctly found largest prime under {target_num}: {expected_prime}")
    sys.exit(0)