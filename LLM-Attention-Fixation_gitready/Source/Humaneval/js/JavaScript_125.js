/* Given a string of words, return a list of words split on whitespace, if no whitespaces exists in the text you
  should split on commas ',' if no commas exists you should return the number of lower-case letters with odd order in the
  alphabet, ord('a') = 0, ord('b') = 1, ... ord('z') = 25
  Examples
  splitWords("Hello world!") ➞ ["Hello", "world!"]
  splitWords("Hello,world!") ➞ ["Hello", "world!"]
  splitWords("abcdef") == 3
  */
const splitWords = (txt) => {

  let t = txt.split(/\s/)
  if (t.length > 1) {
    return t
  } else {
    t = txt.split(/,/)
    if (t.length > 1) {
      return t
    } else {
      let p = 0
      for (let i = 0; i < txt.length; i++) {
        let m = txt[i].charCodeAt()
        if (m >= 97 && m <= 122 && m % 2 == 0) {
          p++
        }
      }
      return p
    }
  }
}

const testSplitWords = () => {
  console.assert(
    JSON.stringify(splitWords('Hello world!')) ===
    JSON.stringify(['Hello', 'world!'])
  )
  console.assert(
    JSON.stringify(splitWords('Hello,world!')) ===
    JSON.stringify(['Hello', 'world!'])
  )
  console.assert(
    JSON.stringify(splitWords('Hello world,!')) ===
    JSON.stringify(['Hello', 'world,!'])
  )
  console.assert(
    JSON.stringify(splitWords('Hello,Hello,world !')) ===
    JSON.stringify(['Hello,Hello,world', '!'])
  )
  console.assert(JSON.stringify(splitWords('abcdef')) === JSON.stringify(3))
  console.assert(JSON.stringify(splitWords('aaabb')) === JSON.stringify(2))
  console.assert(JSON.stringify(splitWords('aaaBb')) === JSON.stringify(1))
  console.assert(JSON.stringify(splitWords('')) === JSON.stringify(0))
}

testSplitWords()
