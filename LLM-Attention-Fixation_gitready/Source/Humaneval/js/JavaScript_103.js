/*You are given two positive integers n and m, and your task is to compute the
  average of the integers from n through m (including n and m). 
  Round the answer to the nearest integer and convert that to binary.
  If n is greater than m, return -1.
  Example:
  roundedAvg(1, 5) => "0b11"
  roundedAvg(7, 5) => -1
  roundedAvg(10, 20) => "0b1111"
  roundedAvg(20, 33) => "0b11010"
  */
const roundedAvg = (n, m) => {

  if (n > m) { return -1 }
  let k = (n + m) / 2
  if (k % 1 != 0) { k = (n + m + 1) / 2 }
  return '0b' + k.toString(2)
}

const testRoundedAvg = () => {
  console.assert(roundedAvg(1, 5) === '0b11')
  console.assert(roundedAvg(7, 13) === '0b1010')
  console.assert(roundedAvg(964, 977) === '0b1111001011')
  console.assert(roundedAvg(996, 997) === '0b1111100101')
  console.assert(roundedAvg(560, 851) === '0b1011000010')
  console.assert(roundedAvg(185, 546) === '0b101101110')
  console.assert(roundedAvg(362, 496) === '0b110101101')
  console.assert(roundedAvg(350, 902) === '0b1001110010')
  console.assert(roundedAvg(197, 233) === '0b11010111')
  console.assert(roundedAvg(7, 5) === -1)
  console.assert(roundedAvg(5, 1) === -1)
  console.assert(roundedAvg(5, 5) === '0b101')
}

testRoundedAvg()
