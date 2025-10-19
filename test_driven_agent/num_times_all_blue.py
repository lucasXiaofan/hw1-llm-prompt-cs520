class Solution:
    def numTimesAllBlue(self, light):
        max_light = 0
        count = 0
        for i, bulb in enumerate(light):
            max_light = max(max_light, bulb)
            if max_light == i + 1:
                count += 1
        return count

# Tests
def test_numTimesAllBlue():
    solution = Solution()
    # Test case 1
    assert solution.numTimesAllBlue([2,1,3,5,4]) == 3
    # Test case 2
    assert solution.numTimesAllBlue([3,2,4,1,5]) == 2
    # Test case 3
    assert solution.numTimesAllBlue([4,1,2,3]) == 1
    # Test case 4
    assert solution.numTimesAllBlue([2,1,4,3,6,5]) == 3
    # Test case 5
    assert solution.numTimesAllBlue([1,2,3,4,5,6]) == 6
    print("All tests passed!")

if __name__ == "__main__":
    test_numTimesAllBlue()
