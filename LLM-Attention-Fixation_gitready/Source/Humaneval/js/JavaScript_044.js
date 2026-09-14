/*Change numerical base of input number x to base.
  return string representation after the conversion.
  base numbers are less than 10.
  >>> changeBase(8, 3)
  '22'
  >>> changeBase(8, 2)
  '1000'
  >>> changeBase(7, 2)
  '111'
  */
const changeBase = (x, base) => {

  var ret = "";
  while (x > 0) {
    ret = (x % base).toString() + ret;
    x = Math.floor(x / base);
  }
  return ret;
}

const testChangeBase = () => {
  console.assert(changeBase(8, 3) === '22')
  console.assert(changeBase(9, 3) === '100')
  console.assert(changeBase(234, 2) === '11101010')
  console.assert(changeBase(16, 2) === '10000')
  console.assert(changeBase(8, 2) === '1000')
  console.assert(changeBase(7, 2) === '111')

  for (let i = 2; i < 8; i++) {
    console.assert(changeBase(i, i + 1) === i.toString())
  }
}

testChangeBase()
