/*Return the largest prime factor of n. Assume n > 1 and is not a prime.
  >>> largestPrimeFactor(13195)
  29
  >>> largestPrimeFactor(2048)
  2
  */
const largestPrimeFactor = (n) => {

  var isPrime = function (k) {
    if (k < 2)
      return false;
    for (let i = 2; i < k - 1; i++)
      if (k % i == 0)
        return false;
    return true;
  }

  var largest = 1;
  for (let j = 2; j < n + 1; j++)
    if (n % j == 0 && isPrime(j))
      largest = Math.max(largest, j);
  return largest;
}

const testLargestPrimeFactor = () => {
  console.assert(largestPrimeFactor(15) === 5)
  console.assert(largestPrimeFactor(27) === 3)
  console.assert(largestPrimeFactor(63) === 7)
  console.assert(largestPrimeFactor(330) === 11)
  console.assert(largestPrimeFactor(13195) === 29)
}

testLargestPrimeFactor()
