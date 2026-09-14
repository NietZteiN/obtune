/* Filter given list of any python values only for integers
  >>> filterIntegers(['a', 3.14, 5])
  [5]
  >>> filterIntegers([1, 2, 3, 'abc', {}, []])
  [1, 2, 3]
  */
const filterIntegers = (values) => {

  return values.filter(x => Number.isInteger(x));
}

const testFilterIntegers = () => {
  console.assert(JSON.stringify(filterIntegers([])) === JSON.stringify([]))
  console.assert(
    JSON.stringify(filterIntegers([4, {}, [], 23.2, 9, 'adasd'])) ===
      JSON.stringify([4, 9])
  )
  console.assert(
    JSON.stringify(filterIntegers([3, 'c', 3, 3, 'a', 'b'])) ===
      JSON.stringify([3, 3, 3])
  )
}

testFilterIntegers()
