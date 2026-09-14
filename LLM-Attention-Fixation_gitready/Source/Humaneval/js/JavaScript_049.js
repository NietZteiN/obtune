/*Return 2^n modulo p (be aware of numerics).
  >>> modp(3, 5)
  3
  >>> modp(1101, 101)
  2
  >>> modp(0, 101)
  1
  >>> modp(3, 11)
  8
  >>> modp(100, 101)
  1
  */
const modp = (n, p) => {

  var ret = 1;
  for (let i = 0; i < n; i++)
    ret = (2 * ret) % p;
  return ret;
}

const testModp = () => {
  console.assert(modp(3, 5) === 3)
  console.assert(modp(1101, 101) === 2)
  console.assert(modp(0, 101) === 1)
  console.assert(modp(3, 11) === 8)
  console.assert(modp(100, 101) === 1)
  console.assert(modp(30, 5) === 4)
  console.assert(modp(31, 5) === 3)
}

testModp()
