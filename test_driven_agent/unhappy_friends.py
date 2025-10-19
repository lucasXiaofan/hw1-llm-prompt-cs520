from typing import List
import unittest

class Solution:
    def unhappyFriends(self, n: int, preferences: List[List[int]], pairs: List[List[int]]) -> int:
        pair_map = {}
        for x, y in pairs:
            pair_map[x] = y
            pair_map[y] = x
        
        unhappy = set()
        
        for x in range(n):
            y = pair_map[x]
            for u in preferences[x]:
                if u == y:
                    break
                v = pair_map[u]
                if preferences[u].index(x) < preferences[u].index(v):
                    unhappy.add(x)
                    break
        
        return len(unhappy)

class TestSolution(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_example_1(self):
        n = 4
        preferences = [[1, 2, 3], [3, 2, 0], [3, 1, 0], [1, 2, 0]]
        pairs = [[0, 1], [2, 3]]
        self.assertEqual(self.solution.unhappyFriends(n, preferences, pairs), 2)
    
    def test_example_2(self):
        n = 2
        preferences = [[1], [0]]
        pairs = [[1, 0]]
        self.assertEqual(self.solution.unhappyFriends(n, preferences, pairs), 0)
    
    def test_example_3(self):
        n = 4
        preferences = [[1, 3, 2], [2, 3, 0], [1, 3, 0], [0, 2, 1]]
        pairs = [[1, 3], [0, 2]]
        self.assertEqual(self.solution.unhappyFriends(n, preferences, pairs), 4)

if __name__ == "__main__":
    unittest.main()
