/*Return true if a given number is prime, and false otherwise.
  >>> isPrime(6)
  false
  >>> isPrime(101)
  true
  >>> isPrime(11)
  true
  >>> isPrime(13441)
  true
  >>> isPrime(61)
  true
  >>> isPrime(4)
  false
  >>> isPrime(1)
  false
  */
const isPrime = (n) => {

  if (n < 2)
    return false;
  for (let k = 2; k < n - 1; k++)
    if (n % k == 0)
      return false;
  return true;
}

const testIsPrime = () => {
  console.assert(isPrime(6) === false)
  console.assert(isPrime(101) === true)
  console.assert(isPrime(11) === true)
  console.assert(isPrime(13441) === true)
  console.assert(isPrime(61) === true)
  console.assert(isPrime(4) === false)
  console.assert(isPrime(1) === false)
  console.assert(isPrime(5) === true)
  console.assert(isPrime(11) === true)
  console.assert(isPrime(17) === true)
  console.assert(isPrime(5 * 17) === false)
  console.assert(isPrime(11 * 7) === false)
  console.assert(isPrime(13441 * 19) === false)
}

testIsPrime()
