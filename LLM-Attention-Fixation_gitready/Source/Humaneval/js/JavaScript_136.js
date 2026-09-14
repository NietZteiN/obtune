/* Create a function that returns a tuple (a, b), where 'a' is
  the largest of negative integers, and 'b' is the smallest
  of positive integers in a list.
  If there is no negative or positive integers, return them as null.
  Examples:
  largestSmallestIntegers([2, 4, 1, 3, 5, 7]) == (null, 1)
  largestSmallestIntegers([]) == (null, null)
  largestSmallestIntegers([0]) == (null, null)
  */
const largestSmallestIntegers = (lst) => {

  let a = Infinity
  let b = -Infinity
  for (let i = 0; i < lst.length; i++) {
    if (lst[i] > 0 && lst[i] < a) { a = lst[i] }
    if (lst[i] < 0 && lst[i] > b) { b = lst[i] }
  }
  if (a == Infinity) { a = null }
  if (b == -Infinity) { b = null }
  return (b, a)
}

const testLargestSmallestIntegers = () => {
  console.assert(
    JSON.stringify(largestSmallestIntegers([2, 4, 1, 3, 5, 7])) ===
    JSON.stringify((null, 1))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([2, 4, 1, 3, 5, 7, 0])) ===
    JSON.stringify((null, 1))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([1, 3, 2, 4, 5, 6, -2])) ===
    JSON.stringify((-2, 1))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([4, 5, 3, 6, 2, 7, -7])) ===
    JSON.stringify((-7, 2))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([7, 3, 8, 4, 9, 2, 5, -9])) ===
    JSON.stringify((-9, 2))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([])) === JSON.stringify((null, null))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([0])) ===
    JSON.stringify((null, null))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([-1, -3, -5, -6])) ===
    JSON.stringify((-1, null))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([-1, -3, -5, -6, 0])) ===
    JSON.stringify((-1, null))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([-6, -4, -4, -3, 1])) ===
    JSON.stringify((-3, 1))
  )
  console.assert(
    JSON.stringify(largestSmallestIntegers([-6, -4, -4, -3, -100, 1])) ===
    JSON.stringify((-3, 1))
  )
}

testLargestSmallestIntegers()
