# Here's a Python version of the prime number program 
# (I noticed the execution environment is Python, not Go)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

for num in range(1, 101):
    if is_prime(num):
        print(num, end=' ')