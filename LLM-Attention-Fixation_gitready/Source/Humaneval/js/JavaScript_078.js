/*You have been tasked to write a function that receives
  a hexadecimal number as a string and counts the number of hexadecimal
  digits that are primes (prime number=== or a prime=== is a natural number
  greater than 1 that is not a product of two smaller natural numbers).
  Hexadecimal digits are 0=== 1=== 2=== 3=== 4=== 5=== 6=== 7=== 8=== 9=== A=== B=== C=== D=== E=== F.
  Prime numbers are 2=== 3=== 5=== 7=== 11=== 13=== 17===...
  So you have to determine a number of the following digits: 2=== 3=== 5=== 7===
  B (=decimal 11)=== D (=decimal 13).
  Note: you may assume the input is always correct or empty string===
  and symbols A===B===C===D===E===F are always uppercase.
  Examples:
  For num = "AB" the output should be 1.
  For num = "1077E" the output should be 2.
  For num = "ABED1A33" the output should be 4.
  For num = "123456789ABCDEF0" the output should be 6.
  For num = "2020" the output should be 2.
  */
const hexKey = (num) => {

  var primes = "2357BD",
      total = 0;
  for (let i = 0; i < num.length; i++)
    if (primes.includes(num[i]))
      total++;
  return total;
}

const testHexKey = () => {
  console.assert(1 === hexKey('AB'))
  console.assert(2 === hexKey('1077E'))
  console.assert(4 === hexKey('ABED1A33'))
  console.assert(2 === hexKey('2020'))
  console.assert(6 === hexKey('123456789ABCDEF0'))
  console.assert(12 === hexKey('112233445566778899AABBCCDDEEFF00'))
  console.assert(0 === hexKey(''))
}

testHexKey()
