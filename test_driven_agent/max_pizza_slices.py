from typing import List

def maxSizeSlices(slices: List[int]) -> int:
    def dp_helper(arr):
        n = len(arr)
        k = len(slices) // 3
        dp = [[0]*(k+1) for _ in range(n+1)]
        
        for i in range(1, n+1):
            for j in range(1, k+1):
                if i >= 2:
                    dp[i][j] = max(dp[i-1][j], dp[i-2][j-1] + arr[i-1])
                else:
                    dp[i][j] = max(dp[i-1][j], arr[i-1])
        return dp[n][k]
    
    return max(dp_helper(slices[:-1]), dp_helper(slices[1:]))

# Test cases
def test_maxSizeSlices():
    assert maxSizeSlices([1, 2, 3, 4, 5, 6]) == 10, "Test case 1 failed"
    assert maxSizeSlices([8, 9, 8, 6, 1, 1]) == 16, "Test case 2 failed"
    assert maxSizeSlices([4, 1, 2, 5, 8, 3, 1, 9, 7]) == 21, "Test case 3 failed"
    assert maxSizeSlices([3, 1, 2]) == 3, "Test case 4 failed"
    print("All test cases passed successfully.")

if __name__ == "__main__":
    test_maxSizeSlices()
