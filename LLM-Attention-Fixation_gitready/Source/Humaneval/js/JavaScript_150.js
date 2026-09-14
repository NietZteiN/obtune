/*A simple program which should return the value of x if n is 
  a prime number and should return the value of y otherwise.

  Examples:
  for xOrY(7, 34, 12) == 34
  for xOrY(15, 8, 5) == 5
  
  */
const xOrY = (n, x, y) => {

  let len = n
  if (len == 1 || len == 0) { return y }
  for (let i = 2; i * i <= len; i++) {
    if (len % i == 0) { return y }
  }
  return x
}

const testXOrY = () => {
  console.assert(xOrY(7, 34, 12) === 34)
  console.assert(xOrY(15, 8, 5) === 5)
  console.assert(xOrY(3, 33, 5212) === 33)
  console.assert(xOrY(1259, 3, 52) === 3)
  console.assert(xOrY(7919, -1, 12) === -1)
  console.assert(xOrY(3609, 1245, 583) === 583)
  console.assert(xOrY(91, 56, 129) === 129)
  console.assert(xOrY(6, 34, 1234) === 1234)
  console.assert(xOrY(1, 2, 0) === 0)
  console.assert(xOrY(2, 2, 0) === 2)
}

testXOrY()
