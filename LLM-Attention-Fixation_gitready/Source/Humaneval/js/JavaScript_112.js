/*Task
  We are given two strings s and c, you have to deleted all the characters in s that are equal to any character in c
  then check if the result string is palindrome.
  A string is called palindrome if it reads the same backward as forward.
  You should return a tuple containing the result string and true/false for the check.
  Example
  For s = "abcde", c = "ae", the result should be ('bcd',false)
  For s = "abcdef", c = "b"  the result should be ('acdef',false)
  For s = "abcdedcba", c = "ab", the result should be ('cdedc',true)
  */
const reverseDelete = (s, c) => {

  let t = ''
  for (let i = 0; i < s.length; i++) {
    let y = 1
    for (let j = 0; j < c.length; j++) {
      if (s[i] == c[j]) {
        y = 0
      }
    }
    if (y == 1) {
      t += s[i]
    }
  }
  let z = 1
  for (let i = 0; i < t.length; i++) {
    if (t[i] != t[t.length - i - 1]) {
      z = 0
    }
  }
  if (z == 0) {
    return (z, false)
  }
  return (z, true)
}

const testReverseDelete = () => {
  console.assert(JSON.stringify(reverseDelete('abcde', 'ae'))) ===
    JSON.stringify(['bcd', false])
  console.assert(JSON.stringify(reverseDelete('abcdef', 'b'))) ===
    JSON.stringify(['acdef', false])
  console.assert(JSON.stringify(reverseDelete('abcdedcba', 'ab'))) ===
    JSON.stringify(['cdedc', true])
  console.assert(JSON.stringify(reverseDelete('dwik', 'w'))) ===
    JSON.stringify(['dik', false])
  console.assert(JSON.stringify(reverseDelete('a', 'a'))) ===
    JSON.stringify(['', true])
  console.assert(JSON.stringify(reverseDelete('abcdedcba', ''))) ===
    JSON.stringify(['abcdedcba', true])
  console.assert(JSON.stringify(reverseDelete('abcdedcba', 'v'))) ===
    JSON.stringify(['abcdedcba', true])
  console.assert(JSON.stringify(reverseDelete('vabba', 'v'))) ===
    JSON.stringify(['abba', true])
  console.assert(JSON.stringify(reverseDelete('mamma', 'mia'))) ===
    JSON.stringify(['', true])
}

testReverseDelete()
