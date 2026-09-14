/*
  removeVowels is a function that takes string and returns string without vowels.
  >>> removeVowels('')
  ''
  >>> removeVowels("abcdef\nghijklm")
  'bcdf\nghjklm'
  >>> removeVowels('abcdef')
  'bcdf'
  >>> removeVowels('aaaaa')
  ''
  >>> removeVowels('aaBAA')
  'B'
  >>> removeVowels('zbcd')
  'zbcd'
  */
const removeVowels = (text) => {

  return text.split("")
             .filter(s => !["a", "e", "i", "o", "u"]
                      .includes(s.toLowerCase())
                    )
             .join("")
}

const testRemoveVowels = () => {
  console.assert(removeVowels('') === '')
  console.assert(removeVowels('abcdef\nghijklm') === 'bcdf\nghjklm')
  console.assert(removeVowels('fedcba') === 'fdcb')
  console.assert(removeVowels('eeeee') === '')
  console.assert(removeVowels('acBAA') === 'cB')
  console.assert(removeVowels('EcBOO') === 'cB')
  console.assert(removeVowels('ybcd') === 'ybcd')
}

testRemoveVowels()
