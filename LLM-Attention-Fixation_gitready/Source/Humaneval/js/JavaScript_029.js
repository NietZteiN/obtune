/* Filter an input list of strings only for ones that start with a given prefix.
  >>> filterByPrefix([], 'a')
  []
  >>> filterByPrefix(['abc', 'bcd', 'cde', 'array'], 'a')
  ['abc', 'array']
  */
const filterByPrefix = (strings, prefix) => {

  return strings.filter(x => x.startsWith(prefix));
}

const testFilterByPrefix = () => {
  console.assert(
    JSON.stringify(filterByPrefix([], 'john')) === JSON.stringify([])
  )
  console.assert(
    JSON.stringify(
      filterByPrefix(['xxx', 'asd', 'xxy', 'john doe', 'xxxAAA', 'xxx'], 'xxx')
    ) === JSON.stringify(['xxx', 'xxxAAA', 'xxx'])
  )
}

testFilterByPrefix()
