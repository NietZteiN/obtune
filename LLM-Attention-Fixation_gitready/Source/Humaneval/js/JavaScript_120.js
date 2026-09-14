/*
  Given an array arr of integers and a positive integer k, return a sorted list 
  of length k with the maximum k numbers in arr.

  Example 1:

      Input: arr = [-3, -4, 5], k = 3
      Output: [-4, -3, 5]

  Example 2:

      Input: arr = [4, -4, 4], k = 2
      Output: [4, 4]

  Example 3:

      Input: arr = [-3, 2, 1, 2, -1, -2, 1], k = 1
      Output: [2]

  Note:
      1. The length of the array will be in the range of [1, 1000].
      2. The elements in the array will be in the range of [-1000, 1000].
      3. 0 <= k <= len(arr)
  */
const maximum = (arr, k) => {

  let p = arr
  for (let j = 0; j < p.length; j++) {
    let ind = j
    for (let k = j + 1; k < p.length; k++) {
      if (p[k] < p[ind]) {
        ind = k
      }
    }
    if (ind > j) {
      let tmp = p[j]
      p[j] = p[ind]
      p[ind] = tmp
    }
  }
  if (k == 0) { return [] }
  return p.slice(-k)
}

const testMaximum = () => {
  console.assert(
    JSON.stringify(maximum([-3, -4, 5], 3)) === JSON.stringify([-4, -3, 5])
  )
  console.assert(
    JSON.stringify(maximum([4, -4, 4], 2)) === JSON.stringify([4, 4])
  )
  console.assert(
    JSON.stringify(maximum([-3, 2, 1, 2, -1, -2, 1], 1)) === JSON.stringify([2])
  )
  console.assert(
    JSON.stringify(maximum([123, -123, 20, 0, 1, 2, -3], 3)) ===
    JSON.stringify([2, 20, 123])
  )
  console.assert(
    JSON.stringify(maximum([-123, 20, 0, 1, 2, -3], 4)) ===
    JSON.stringify([0, 1, 2, 20])
  )
  console.assert(
    JSON.stringify(maximum([5, 15, 0, 3, -13, -8, 0], 7)) ===
    JSON.stringify([-13, -8, 0, 0, 3, 5, 15])
  )
  console.assert(
    JSON.stringify(maximum([-1, 0, 2, 5, 3, -10], 2)) === JSON.stringify([3, 5])
  )
  console.assert(
    JSON.stringify(maximum([1, 0, 5, -7], 1)) === JSON.stringify([5])
  )
  console.assert(JSON.stringify(maximum([4, -4], 2)) === JSON.stringify([-4, 4]))
  console.assert(
    JSON.stringify(maximum([-10, 10], 2)) === JSON.stringify([-10, 10])
  )
  console.assert(
    JSON.stringify(maximum([1, 2, 3, -23, 243, -400, 0], 0)) ===
    JSON.stringify([])
  )
}

testMaximum()
