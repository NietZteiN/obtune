/*Create a function which returns the largest index of an element which
  is not greater than or equal to the element immediately preceding it. If
  no such element exists then return -1. The given array will not contain
  duplicate values.

  Examples:
  canArrange([1,2,4,3,5]) = 3
  canArrange([1,2,3]) = -1
  */
const canArrange = (arr) => {

  if (arr.length == 0) { return -1 }
  for (let i = arr.length - 1; i > 0; i--) {
    if (arr[i] < arr[i - 1]) { return i }
  }
  return -1
}

const testCanArrange = () => {
  console.assert(canArrange([1, 2, 4, 3, 5]) === 3)
  console.assert(canArrange([1, 2, 4, 5]) === -1)
  console.assert(canArrange([1, 4, 2, 5, 6, 7, 8, 9, 10]) === 2)
  console.assert(canArrange([4, 8, 5, 7, 3]) === 4)
  console.assert(canArrange([]) === -1)
}

testCanArrange()
