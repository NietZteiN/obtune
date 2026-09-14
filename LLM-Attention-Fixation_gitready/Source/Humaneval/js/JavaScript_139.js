/*The Brazilian factorial is defined as:
  brazilian_factorial(n) = n! * (n-1)! * (n-2)! * ... * 1!
  where n > 0

  For example:
  >>> specialFactorial(4)
  288

  The function will receive an integer as input and should return the special
  factorial of this integer.
  */
const specialFactorial = (n) => {

  let p = 1;
  let t = 1;
  while (n > 1) {
    let y = p;
    while (y > 0) {
      y--;
      t *= n;
    }
    p++;
    n--;
  }
  return t
}

const testSpecialFactorial = () => {
  console.assert(specialFactorial(4) === 288)
  console.assert(specialFactorial(5) === 34560)
  console.assert(specialFactorial(7) === 125411328000)
  console.assert(specialFactorial(1) === 1)
}

testSpecialFactorial()
