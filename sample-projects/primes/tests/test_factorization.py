
import unittest
from src.factorization import is_prime, prime_factorize

class TestFactorization(unittest.TestCase):

    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertTrue(is_prime(5))
        self.assertTrue(is_prime(17))
        self.assertTrue(is_prime(97))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(100))
        self.assertFalse(is_prime(999))

    def test_prime_factorize_small_numbers(self):
        self.assertEqual(prime_factorize(1), [])
        self.assertEqual(prime_factorize(2), [2])
        self.assertEqual(prime_factorize(3), [3])
        self.assertEqual(prime_factorize(4), [2, 2])
        self.assertEqual(prime_factorize(12), [2, 2, 3])
        self.assertEqual(prime_factorize(15), [3, 5])

    def test_prime_factorize_large_numbers(self):
        self.assertEqual(prime_factorize(100), [2, 2, 5, 5])
        self.assertEqual(prime_factorize(1234), [2, 617])
        self.assertEqual(prime_factorize(123456), [2, 2, 2, 2, 2, 2, 3, 643])
        self.assertEqual(prime_factorize(9876543210), [2, 3, 3, 5, 17, 17, 379721])

    def test_prime_factorize_prime_numbers(self):
        self.assertEqual(prime_factorize(2), [2])
        self.assertEqual(prime_factorize(17), [17])
        self.assertEqual(prime_factorize(97), [97])
        self.assertEqual(prime_factorize(10007), [10007])

    def test_prime_factorize_edge_cases(self):
        self.assertEqual(prime_factorize(1), [])
        self.assertEqual(prime_factorize(2), [2])
        # Test a very large number (close to sys.maxsize on many systems)
        self.assertEqual(prime_factorize(9223372036854775807), [9223372036854775807])

    def test_prime_factorize_invalid_input(self):
        with self.assertRaises(ValueError):
            prime_factorize(0)
        with self.assertRaises(ValueError):
            prime_factorize(-1)
        with self.assertRaises(ValueError):
            prime_factorize(1.5)
        with self.assertRaises(ValueError):
            prime_factorize("not a number")

if __name__ == '__main__':
    unittest.main()
