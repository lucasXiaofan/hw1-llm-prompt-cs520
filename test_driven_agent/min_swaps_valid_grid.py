from typing import List

class Solution:
    def minSwaps(self, grid: List[List[int]]) -> int:
        """Given an n x n binary grid, in one step you can choose two adjacent rows of the grid and swap them.
        A grid is said to be valid if all the cells above the main diagonal are zeros.
        Return the minimum number of steps needed to make the grid valid, or -1 if the grid cannot be valid.
        """
        n = len(grid)
        # For each row, find the number of trailing zeros (rightmost ones)
        # For grid to be valid, row i must have >= (n - 1 - i) trailing zeros
        # We represent the requirement for each row
        required = [n - 1 - i for i in range(n)]
        # For each row, count trailing zeros
        counts = []
        for row in grid:
            count = 0
            for j in range(len(row) - 1, -1, -1):
                if row[j] == 0:
                    count += 1
                else:
                    break
            counts.append(count)
        
        swaps = 0
        
        for i in range(n):
            # Find the first row that satisfies the requirement for current position i
            found = -1
            for j in range(i, n):
                if counts[j] >= required[i]:
                    found = j
                    break
            if found == -1:
                return -1
            # Swap rows to bring the found row to position i
            for j in range(found, i, -1):
                counts[j], counts[j - 1] = counts[j - 1], counts[j]
                swaps += 1
        return swaps

if __name__ == "__main__":
    import unittest

    class TestMinSwaps(unittest.TestCase):
        def test_example1(self):
            grid = [[0, 0, 1], [1, 1, 0], [1, 0, 0]]
            self.assertEqual(Solution().minSwaps(grid), 3)
        
        def test_example2(self):
            grid = [[0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0]]
            self.assertEqual(Solution().minSwaps(grid), -1)
        
        def test_example3(self):
            grid = [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
            self.assertEqual(Solution().minSwaps(grid), 0)

    unittest.main(argv=['first-arg-is-ignored'], exit=False)
