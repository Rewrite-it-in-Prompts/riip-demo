# Prime Factorization Utility

## Project Description and Purpose

This command-line utility is designed to find and display the prime factors of any given positive integer. It provides a quick and efficient way for users to decompose numbers into their prime components. The tool is implemented in Python and focuses on performance and usability.

## Installation Instructions

1. Ensure you have Python 3.8 or higher installed on your system.
2. Clone this repository or download the source files.
3. Navigate to the project directory in your terminal.

No additional installation steps are required as the utility uses only Python standard libraries.

## Usage Examples

To use the Prime Factorization Utility, run the `main.py` script with a positive integer as an argument:

```
python src/main.py <number>
```

Examples:

```
python src/main.py 24
Output: Prime factors: 2 × 2 × 2 × 3

python src/main.py 100
Output: Prime factors: 2 × 2 × 5 × 5

python src/main.py 17
Output: Prime factors: 17
```

## Dependencies and Requirements

- Python 3.8 or higher
- No external libraries are required

## Implementation Details

The utility uses the trial division algorithm for prime factorization. This method is efficient for smaller numbers and provides a good balance between simplicity and performance. The implementation includes:

- Input validation and error handling
- Efficient prime checking function
- Trial division algorithm for factorization
- Clear output formatting

The code is structured into two main files:
- `main.py`: Handles command-line interface and user interaction
- `factorization.py`: Contains the core logic for prime factorization

The implementation follows PEP 8 style guidelines and includes type hints for improved readability and maintainability.

