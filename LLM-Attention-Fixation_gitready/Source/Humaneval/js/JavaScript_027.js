/* For a given string, flip lowercase characters to uppercase and uppercase to lowercase.
  >>> flipCase('Hello')
  'hELLO'
  */
const flipCase = (string) => {

  return string.split('')
          .map(x => (x.toUpperCase() == x ? x.toLowerCase() : x.toUpperCase()))
          .join('');
}

const testFlipCase = () => {
  console.assert(flipCase('') === '')
  console.assert(flipCase('Hello!') === 'hELLO!')
  console.assert(
    flipCase(
      'These violent delights have violent ends') ===
        'tHESE VIOLENT DELIGHTS HAVE VIOLENT ENDS'
  )
}

testFlipCase()
