/*Write a function that takes a string and returns true if the string
  length is a prime number or false otherwise
  Examples
  primeLength('Hello') == true
  primeLength('abcdcba') == true
  primeLength('kittens') == true
  primeLength('orange') == false
  */
const primeLength = (string) => {

  let len = string.length
  if (len == 1 || len == 0) { return false }
  for (let i = 2; i * i <= len; i++) {
    if (len % i == 0) { return false }
  }
  return true
}

const testPrimeLength = () => {
  console.assert(primeLength('Hello') === true)
  console.assert(primeLength('abcdcba') === true)
  console.assert(primeLength('kittens') === true)
  console.assert(primeLength('orange') === false)
  console.assert(primeLength('wow') === true)
  console.assert(primeLength('world') === true)
  console.assert(primeLength('MadaM') === true)
  console.assert(primeLength('Wow') === true)
  console.assert(primeLength('') === false)
  console.assert(primeLength('HI') === true)
  console.assert(primeLength('go') === true)
  console.assert(primeLength('gogo') === false)
  console.assert(primeLength('aaaaaaaaaaaaaaa') === false)
  console.assert(primeLength('Madam') === true)
  console.assert(primeLength('M') === false)
  console.assert(primeLength('0') === false)
}

testPrimeLength()
