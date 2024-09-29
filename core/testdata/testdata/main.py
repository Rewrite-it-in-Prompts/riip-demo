def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

for n in range(100, 1, -1):
    if is_prime(n):
        print(n)
        break