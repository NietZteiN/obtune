/*Evaluate whether the given number n can be written as the sum of exactly 4 positive even numbers
  Example
  isEqualToSumEven(4) == false
  isEqualToSumEven(6) == false
  isEqualToSumEven(8) == true
  */
const isEqualToSumEven = (n) => {

  return (n >= 8 && n % 2 == 0)
}

const testIsEqualToSumEven = () => {
  console.assert(isEqualToSumEven(4) === false)
  console.assert(isEqualToSumEven(6) === false)
  console.assert(isEqualToSumEven(8) === true)
  console.assert(isEqualToSumEven(10) === true)
  console.assert(isEqualToSumEven(11) === false)
  console.assert(isEqualToSumEven(12) === true)
  console.assert(isEqualToSumEven(13) === false)
  console.assert(isEqualToSumEven(16) === true)
}

testIsEqualToSumEven()
