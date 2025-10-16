import unittest 
from pluck_smallest_even import pluck_smallest_even 
 
class TestPluckSmallestEven(unittest.TestCase): 
    def test_example1(self): 
        self.assertEqual(pluck_smallest_even([4, 2, 3]), [2, 1]) 
    def test_example2(self): 
        self.assertEqual(pluck_smallest_even([1, 2, 3]), [2, 1]) 
    def test_example3(self): 
        self.assertEqual(pluck_smallest_even([]), []) 
    def test_example4(self): 
        self.assertEqual(pluck_smallest_even([5, 0, 3, 0, 4, 2]), [0, 1]) 
    def test_no_even_numbers(self): 
        self.assertEqual(pluck_smallest_even([1, 3, 5]), []) 
    def test_single_even_number(self): 
        self.assertEqual(pluck_smallest_even([7, 4, 9]), [4, 1]) 
    def test_multiple_same_even_numbers(self): 
        self.assertEqual(pluck_smallest_even([2, 2, 4, 2]), [2, 0]) 
 
if __name__ == '__main__': 
    unittest.main() 
