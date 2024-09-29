#!/usr/bin/env python3

from typing import List
import math

def is_prime(n: int) -> bool:
    """
    Check if a number is prime.

    Args:
        n (int): The number to check.

    Returns:
        bool: True if the number is prime, False otherwise.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def trial_division(n: int) -> List[int]:
    """
    Find prime factors using trial division method.

    Args:
        n (int): The number to factorize.

    Returns:
        List[int]: List of prime factors.
    """
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.append(i)
            n //= i
    
    if n > 2:
        factors.append(n)
    
    return factors

def prime_factorize(n: int) -> List[int]:
    """
    Find the prime factors of a given number.

    Args:
        n (int): The number to factorize.

    Returns:
        List[int]: List of prime factors in ascending order.

    Raises:
        ValueError: If the input is not a positive integer.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Input must be a positive integer.")
    
    if n == 1:
        return []
    
    return trial_division(n)

# Alias for compatibility with main.py
prime_factors = prime_factorize