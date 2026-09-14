/* Given a string, find out how many distinct characters (regardless of case) does it consist of
  >>> countDistinctCharacters('xyzXYZ')
  3
  >>> countDistinctCharacters('Jerry')
  4
  */
const countDistinctCharacters = (string) => {

  return (new Set(string.toLowerCase())).size;

}

const testCountDistinctCharacters = () => {
  console.assert(countDistinctCharacters('') === 0)
  console.assert(countDistinctCharacters('abcde') === 5)
  console.assert(countDistinctCharacters('abcde' + 'cade' + 'CADE') === 5)
  console.assert(countDistinctCharacters('aaaaAAAAaaaa') === 1)
  console.assert(countDistinctCharacters('Jerry jERRY JeRRRY') === 5)
}

testCountDistinctCharacters()
