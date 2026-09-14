/*Write a function that takes an array of numbers as input and returns 
  the number of elements in the array that are greater than 10 and both 
  first and last digits of a number are odd (1, 3, 5, 7, 9).
  For example:
  specialFilter([15, -73, 14, -15]) => 1 
  specialFilter([33, -2, -3, 45, 21, 109]) => 2
  */
const specialFilter = (nums) => {

  let p = 0
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] < 10) { continue }
    let y = nums[i].toString()
    if (Number(y[0]) % 2 == 1 && Number(y[y.length - 1]) % 2 == 1) {
      p++
    }
  }
  return p
}

const testSpecialFilter = () => {
  console.assert(specialFilter([5, -2, 1, -5]) === 0)
  console.assert(specialFilter([15, -73, 14, -15]) === 1)
  console.assert(specialFilter([33, -2, -3, 45, 21, 109]) === 2)
  console.assert(specialFilter([43, -12, 93, 125, 121, 109]) === 4)
  console.assert(specialFilter([71, -2, -33, 75, 21, 19]) === 3)
  console.assert(specialFilter([1]) === 0)
  console.assert(specialFilter([]) === 0)
}

testSpecialFilter()
