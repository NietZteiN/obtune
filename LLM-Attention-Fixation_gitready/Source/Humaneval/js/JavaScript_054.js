/*
  Check if two words have the same characters.
  >>> sameChars('eabcdzzzz', 'dddzzzzzzzddeddabc')
  true
  >>> sameChars('abcd', 'dddddddabc')
  true
  >>> sameChars('dddddddabc', 'abcd')
  true
  >>> sameChars('eabcd', 'dddddddabc')
  false
  >>> sameChars('abcd', 'dddddddabce')
  false
  >>> sameChars('eabcdzzzz', 'dddzzzzzzzddddabc')
  false
  */
const sameChars = (s0, s1) => {

  return JSON.stringify([...new Set(s0)].sort()) === JSON.stringify([...new Set(s1)].sort());
}

const testSameChars = () => {
  console.assert(sameChars('eabcdzzzz', 'dddzzzzzzzddeddabc') === true)
  console.assert(sameChars('abcd', 'dddddddabc') === true)
  console.assert(sameChars('dddddddabc', 'abcd') === true)
  console.assert(sameChars('eabcd', 'dddddddabc') === false)
  console.assert(sameChars('abcd', 'dddddddabcf') === false)
  console.assert(sameChars('eabcdzzzz', 'dddzzzzzzzddddabc') === false)
  console.assert(sameChars('aabb', 'aaccc') === false)
}

testSameChars()
