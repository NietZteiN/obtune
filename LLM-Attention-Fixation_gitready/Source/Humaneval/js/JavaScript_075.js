/*Write a function that returns true if the given number is the multiplication of 3 prime numbers
  and false otherwise.
  Knowing that (a) is less then 100.
  Example:
  isMultiplyPrime(30) == true
  30 = 2 * 3 * 5
  */
const isMultiplyPrime = (a) => {

  var isPrime = function (n) {
    for (let j = 2; j < n; j++)
      if (n % j == 0)
        return false;
    return true;
  }

  for (let i = 2; i < 101; i++) {
    if (!isPrime(i)) continue;
    for (let j = 2; j < 101; j++) {
      if (!isPrime(j)) continue;
      for (let k = 2; k < 101; k++) {
        if (!isPrime(k)) continue;
        if (i*j*k == a)
          return true;
      }
    }
  }
  return false;
}

const testIsMultiplyPrime = () => {
  console.assert(isMultiplyPrime(5) === false)
  console.assert(isMultiplyPrime(30) === true)
  console.assert(isMultiplyPrime(8) === true)
  console.assert(isMultiplyPrime(10) === false)
  console.assert(isMultiplyPrime(125) === true)
  console.assert(isMultiplyPrime(3 * 5 * 7) === true)
  console.assert(isMultiplyPrime(3 * 6 * 7) === false)
  console.assert(isMultiplyPrime(9 * 9 * 9) === false)
  console.assert(isMultiplyPrime(11 * 9 * 9) === false)
  console.assert(isMultiplyPrime(11 * 13 * 7) === true)
}

testIsMultiplyPrime()
