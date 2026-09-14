/* Insert a number 'delimeter' between every two consecutive elements of input list `numbers'
  >>> intersperse([], 4)
  []
  >>> intersperse([1, 2, 3], 4)
  [1, 4, 2, 4, 3]
  */
const intersperse = (numbers, delimeter) => {

  if (!Array.isArray(numbers) || numbers.length == 0)
    return [];
  var result = [];
  for (const n of numbers) {
    result.push(n, delimeter);
  }
  result.pop();
  return result;
}

const testIntersperse = () => {
  console.assert(JSON.stringify(intersperse([], 7)) === JSON.stringify([]))
  console.assert(
    JSON.stringify(
      intersperse([5, 6, 3, 2], 8)) === JSON.stringify([5, 8, 6, 8, 3, 8, 2])
  )
  console.assert(
    JSON.stringify(
      intersperse([2, 2, 2], 2)) === JSON.stringify([2, 2, 2, 2, 2])
  )
}

testIntersperse()
