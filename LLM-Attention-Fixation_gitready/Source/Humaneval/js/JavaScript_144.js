/*Your task is to implement a function that will simplify the expression
  x * n. The function returns true if x * n evaluates to a whole number and false
  otherwise. Both x and n, are string representation of a fraction, and have the following format,
  <numerator>/<denominator> where both numerator and denominator are positive whole numbers.

  You can assume that x, and n are valid fractions, and do not have zero as denominator.

  simplify("1/5", "5/1") = true
  simplify("1/6", "2/1") = false
  simplify("7/10", "10/2") = false
  */
const simplify = (x, n) => {

  let a = x.split(/\//)
  let b = n.split(/\//)
  let m = Number(a[0]) * Number(b[0])
  let r = Number(a[1]) * Number(b[1])
  return m % r == 0
}

const testSimplify = () => {
  console.assert(simplify('1/5', '5/1') === true)
  console.assert(simplify('1/6', '2/1') === false)
  console.assert(simplify('5/1', '3/1') === true)
  console.assert(simplify('7/10', '10/2') === false)
  console.assert(simplify('2/10', '50/10') === true)
  console.assert(simplify('7/2', '4/2') === true)
  console.assert(simplify('11/6', '6/1') === true)
  console.assert(simplify('2/3', '5/2') === false)
  console.assert(simplify('5/2', '3/5') === false)
  console.assert(simplify('2/4', '8/4') === true)
  console.assert(simplify('2/4', '4/2') === true)
  console.assert(simplify('1/5', '5/1') === true)
  console.assert(simplify('1/5', '1/5') === false)
}

testSimplify()
