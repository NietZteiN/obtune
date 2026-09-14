/* Create a function that returns true if the last character
  of a given string is an alphabetical character and is not
  a part of a word, and false otherwise.
  Note: "word" is a group of characters separated by space.
  Examples:
  checkIfLastCharIsALetter("apple pie") ➞ false
  checkIfLastCharIsALetter("apple pi e") ➞ true
  checkIfLastCharIsALetter("apple pi e ") ➞ false
  checkIfLastCharIsALetter("") ➞ false
  */
const checkIfLastCharIsALetter = (txt) => {

  let len = txt.length
  if (len == 0) { return false }
  let y = txt[len - 1].charCodeAt()
  if (len == 1) {
    if ((y >= 65 && y <= 90) || (y >= 97 && y <= 122)) { return true }
    return false
  }
  if (txt[len - 2] == ' ' && ((y >= 65 && y <= 90) || (y >= 97 && y <= 122))) { return true }
  return false
}

const testCheckIfLastCharIsALetter = () => {
  console.assert(checkIfLastCharIsALetter('apple') === false)
  console.assert(checkIfLastCharIsALetter('apple pi e') === true)
  console.assert(checkIfLastCharIsALetter('eeeee') === false)
  console.assert(checkIfLastCharIsALetter('A') === true)
  console.assert(checkIfLastCharIsALetter('Pumpkin pie ') === false)
  console.assert(checkIfLastCharIsALetter('Pumpkin pie 1') === false)
  console.assert(checkIfLastCharIsALetter('') === false)
  console.assert(checkIfLastCharIsALetter('eeeee e ') === false)
  console.assert(checkIfLastCharIsALetter('apple pie') === false)
  console.assert(checkIfLastCharIsALetter('apple pi e ') === false)
}

testCheckIfLastCharIsALetter()
