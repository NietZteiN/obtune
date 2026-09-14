/*Task
  Write a function that takes a string as input and returns the sum of the upper characters only'
  ASCII codes.

  Examples:
      digitSum("") => 0
      digitSum("abAB") => 131
      digitSum("abcCd") => 67
      digitSum("helloE") => 69
      digitSum("woArBld") => 131
      digitSum("aAaaaXa") => 153
  */
const digitSum = (s) => {

  if (s == '') return 0;
  return s.split('').reduce((prev, char) => {
    let ord_char = char.charCodeAt(0)
    return prev + (ord_char > 64 && ord_char < 91 ? ord_char : 0);
  }, 0);
}

const testDigitSum = () => {
  console.assert(digitSum('') === 0)
  console.assert(digitSum('abAB') === 131)
  console.assert(digitSum('abcCd') === 67)
  console.assert(digitSum('helloE') === 69)
  console.assert(digitSum('woArBld') === 131)
  console.assert(digitSum('aAaaaXa') === 153)
  console.assert(digitSum(' How are yOu?') === 151)
  console.assert(digitSum('You arE Very Smart') === 327)
}

testDigitSum()
