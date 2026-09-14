/*sumToN is a function that sums numbers from 1 to n.
  >>> sumToN(30)
  465
  >>> sumToN(100)
  5050
  >>> sumToN(5)
  15
  >>> sumToN(10)
  55
  >>> sumToN(1)
  1
  */
const sumToN = (n) => {

  return n * (n + 1) / 2;
}

const testSumToN = () => {
  console.assert(sumToN(1) === 1)
  console.assert(sumToN(6) === 21)
  console.assert(sumToN(11) === 66)
  console.assert(sumToN(30) === 465)
  console.assert(sumToN(100) === 5050)
}

testSumToN()
