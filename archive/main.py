def main():
    print("Hello from hw1-llm-prompt!")


if __name__ == "__main__":
    from typing import List

    class Solution:
        def maxSizeSlices(self, slices: List[int]) -> int:
            def maxSum(slices: List[int], n: int) -> int:
                m = len(slices)
                # dp[i][j]: max sum using first i slices, choosing j slices
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                for i in range(1, m + 1):
                    for j in range(1, min(i, n) + 1):
                        dp[i][j] = max(
                            dp[i - 1][j],  # skip i-th slice
                            dp[i - 2][j - 1] + slices[i - 1] if i >= 2 else slices[i - 1]
                        )
                return dp[m][n]

            k = len(slices) // 3
            # Case 1: exclude last slice
            case1 = maxSum(slices[:-1], k)
            # Case 2: exclude first slice
            case2 = maxSum(slices[1:], k)
            return max(case1, case2)

    s = Solution()
    print(s.maxSizeSlices([
                    1,
                    2,
                    3,
                    4,
                    5,
                    6
                ]))
