/* For a given number n, find the largest number that divides n evenly, smaller than n
  >>> largestDivisor(15)
  5
  */
const largestDivisor = (n) => {

  for (let i = n - 1; i >= 0; i--)
    if (n % i == 0)
      return i;
}

const testLargestDivisor = () => {
  console.assert(largestDivisor(3) === 1)
  console.assert(largestDivisor(7) === 1)
  console.assert(largestDivisor(10) === 5)
  console.assert(largestDivisor(100) === 50)
  console.assert(largestDivisor(49) === 7)
}

testLargestDivisor()
