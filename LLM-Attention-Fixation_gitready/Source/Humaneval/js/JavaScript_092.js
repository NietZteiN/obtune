/* Create a function that takes 3 numbers.
  Returns true if one of the numbers is equal to the sum of the other two, and all numbers are integers.
  Returns false in any other cases.
  Examples
  anyInt(5, 2, 7) ➞ true
  anyInt(3, 2, 2) ➞ false
  anyInt(3, -2, 1) ➞ true
  anyInt(3.6, -2.2, 2) ➞ false
  */
const anyInt = (x, y, z) => {

  if (x % 1 === 0 && y % 1 === 0 && z % 1 === 0 && (x + y === z || x + z === y || x === y + z)) {
    return true
  }
  return false
}

const testAnyInt = () => {
  console.assert(anyInt(2, 3, 1) === true)
  console.assert(anyInt(2.5, 2, 3) === false)
  console.assert(anyInt(1.5, 5, 3.5) === false)
  console.assert(anyInt(2, 6, 2) === false)
  console.assert(anyInt(4, 2, 2) === true)
  console.assert(anyInt(2.2, 2.2, 2.2) === false)
  console.assert(anyInt(-4, 6, 2) === true)
  console.assert(anyInt(2, 1, 1) === true)
  console.assert(anyInt(3, 4, 7) === true)
  console.assert(anyInt(3.0, 4, 7) === true)
}

testAnyInt()
