/* Concatenate list of strings into a single string
  >>> concatenate([])
  ''
  >>> concatenate(['a', 'b', 'c'])
  'abc'
  */
const concatenate = (strings) => {

  return strings.join('');
}

const testConcatenate = () => {
  console.assert(concatenate([]) === '')
  console.assert(concatenate(['x', 'y', 'z']) === 'xyz')
  console.assert(concatenate(['x', 'y', 'z', 'w', 'k']) === 'xyzwk')
}

testConcatenate()
