
import unittest
from unittest.mock import patch
import sys
from io import StringIO
from src.main import parse_arguments, display_results, main

class TestMain(unittest.TestCase):

    def test_parse_arguments_valid(self):
        with patch('sys.argv', ['script_name', '42']):
            self.assertEqual(parse_arguments(), 42)

    def test_parse_arguments_invalid(self):
        with patch('sys.argv', ['script_name', '-1']):
            with self.assertRaises(SystemExit):
                parse_arguments()

    def test_parse_arguments_non_integer(self):
        with patch('sys.argv', ['script_name', 'abc']):
            with self.assertRaises(SystemExit):
                parse_arguments()

    def test_display_results_normal(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        display_results([2, 2, 3])
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue().strip(), "Prime factors: 2 × 2 × 3")

    def test_display_results_empty(self):
        captured_output = StringIO()
        sys.stdout = captured_output
        display_results([])
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue().strip(), "The number 1 has no prime factors.")

    @patch('src.main.parse_arguments')
    @patch('src.main.prime_factorize')
    def test_main_normal(self, mock_prime_factorize, mock_parse_arguments):
        mock_parse_arguments.return_value = 12
        mock_prime_factorize.return_value = [2, 2, 3]
        
        captured_output = StringIO()
        sys.stdout = captured_output
        main()
        sys.stdout = sys.__stdout__
        
        self.assertEqual(captured_output.getvalue().strip(), "Prime factors: 2 × 2 × 3")

    @patch('src.main.parse_arguments')
    def test_main_value_error(self, mock_parse_arguments):
        mock_parse_arguments.side_effect = ValueError("Test error")
        
        captured_output = StringIO()
        sys.stderr = captured_output
        with self.assertRaises(SystemExit):
            main()
        sys.stderr = sys.__stderr__
        
        self.assertEqual(captured_output.getvalue().strip(), "Error: Test error")

if __name__ == '__main__':
    unittest.main()

