/* Return list of prime factors of given integer in the order from smallest to largest.
  Each of the factors should be listed number of times corresponding to how many times it appeares in factorization.
  Input number should be equal to the product of all factors
  >>> factorize(8)
  [2, 2, 2]
  >>> factorize(25)
  [5, 5]
  >>> factorize(70)
  [2, 5, 7]
  */
const factorize = (n) => {

  var fact = [], i = 2;
  while (i <= Math.sqrt(n) + 1) {
    if (n % i == 0) {
      fact.push(i);
      n = n / i;
    } else {
      i += 1;
    }
  }

  if (n > 1)
    fact.push(n);
  return fact;
}

const testFactorize = () => {
  console.assert(JSON.stringify(factorize(2)) === JSON.stringify([2]))
  console.assert(JSON.stringify(factorize(4)) === JSON.stringify([2, 2]))
  console.assert(JSON.stringify(factorize(8)) === JSON.stringify([2, 2, 2]))
  console.assert(JSON.stringify(factorize(3 * 19)) === JSON.stringify([3, 19]))
  console.assert(
    JSON.stringify(factorize(3 * 19 * 3 * 19)) ===
      JSON.stringify([3, 3, 19, 19])
  )
  console.assert(
    JSON.stringify(factorize(3 * 19 * 3 * 19 * 3 * 19)) ===
      JSON.stringify([3, 3, 3, 19, 19, 19])
  )
  console.assert(
    JSON.stringify(factorize(3 * 19 * 19 * 19)) ===
      JSON.stringify([3, 19, 19, 19])
  )
  console.assert(
    JSON.stringify(factorize(3 * 2 * 3)) === JSON.stringify([2, 3, 3])
  )
}

testFactorize()
