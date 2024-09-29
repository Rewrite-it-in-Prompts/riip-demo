#!/usr/bin/env python3

import sys
import argparse
from typing import List

from prime_factorization import prime_factorize

def parse_arguments() -> int:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(description="Prime Factorization Utility")
    parser.add_argument("number", type=int, help="Positive integer to factorize")
    args = parser.parse_args()

    if args.number <= 0:
        parser.error("Input must be a positive integer.")

    return args.number

def display_results(factors: List[int]) -> None:
    """Format and print the prime factors."""
    if not factors:
        print("The number 1 has no prime factors.")
    else:
        print("Prime factors:", " × ".join(map(str, factors)))

def main() -> None:
    """Main entry point of the program."""
    try:
        number = parse_arguments()
        factors = prime_factorize(number)
        display_results(factors)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()