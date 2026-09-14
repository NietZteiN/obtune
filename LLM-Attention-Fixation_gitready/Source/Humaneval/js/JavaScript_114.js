/*
  Given an array of integers nums, find the minimum sum of any non-empty sub-array
  of nums.
  Example
  minSubArraySum([2, 3, 4, 1, 2, 4]) == 1
  minSubArraySum([-1, -2, -3]) == -6
  */
const minSubArraySum = (nums) => {

  let min = nums[0]
  for (let i = 0; i < nums.length; i++) {
    for (let j = i + 1; j <= nums.length; j++) {
      let s = 0;
      for (let k = i; k < j; k++) {
        s += nums[k]
      }
      if (s < min) { min = s }
    }
  }
  return min
}

const testMinSubArraySum = () => {
  console.assert(minSubArraySum([2, 3, 4, 1, 2, 4]) === 1)
  console.assert(minSubArraySum([-1, -2, -3]) === -6)
  console.assert(minSubArraySum([-1, -2, -3, 2, -10]) === -14)
  console.assert(minSubArraySum([-9999999999999999]) === -9999999999999999)
  console.assert(minSubArraySum([0, 10, 20, 1000000]) === 0)
  console.assert(minSubArraySum([-1, -2, -3, 10, -5]) === -6)
  console.assert(minSubArraySum([100, -1, -2, -3, 10, -5]) === -6)
  console.assert(minSubArraySum([10, 11, 13, 8, 3, 4]) === 3)
  console.assert(minSubArraySum([100, -33, 32, -1, 0, -2]) === -33)
  console.assert(minSubArraySum([-10]) === -10)
  console.assert(minSubArraySum([7]) === 7)
  console.assert(minSubArraySum([1, -1]) === -1)
}

testMinSubArraySum()
