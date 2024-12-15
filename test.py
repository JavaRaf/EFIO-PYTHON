









class Solution(object):
    def twoSum(self, nums, target):
        nums_index = {}
        result = []
        for i,n in enumerate(nums):
            complement = target-n
            if complement in nums_index:
                result.append(nums_index[complement])
                result.append(i)
            else:
                nums_index[n] = i
        return result
    

# Test case

nums = [2, 7, 11, 15]
target = 9
s = Solution()
print(s.twoSum(nums, target))  # Output: [0, 1]
