/*This function takes a list l and returns a list l' such that
  l' is identical to l in the indicies that are not divisible by three, while its values at the indicies that are divisible by three are equal
  to the values of the corresponding indicies of l, but sorted.
  >>> sortThird([1, 2, 3])
  [1, 2, 3]
  >>> sortThird([5, 6, 3, 4, 8, 9, 2])
  [2, 6, 3, 4, 8, 9, 5]
  */
const sortThird = (l) => {

  var three = l.filter((item, index) => index % 3 == 0);
  three.sort((a, b) => (a - b));
  return l.map((item, index) => (index % 3 == 0 ? three[index / 3] : item));
}

const testSortThird = () => {
  console.assert(
    JSON.stringify(sortThird([1, 2, 3])) == JSON.stringify([1, 2, 3])
  )
  console.assert(
    JSON.stringify(sortThird([5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10])) ==
      JSON.stringify([1, 3, -5, 2, -3, 3, 5, 0, 123, 9, -10])
  )
  console.assert(
    JSON.stringify(sortThird([5, 8, -12, 4, 23, 2, 3, 11, 12, -10])) ==
      JSON.stringify([-10, 8, -12, 3, 23, 2, 4, 11, 12, 5])
  )
  console.assert(
    JSON.stringify(sortThird([5, 6, 3, 4, 8, 9, 2])) ==
      JSON.stringify([2, 6, 3, 4, 8, 9, 5])
  )
  console.assert(
    JSON.stringify(sortThird([5, 8, 3, 4, 6, 9, 2])) ==
      JSON.stringify([2, 8, 3, 4, 6, 9, 5])
  )
  console.assert(
    JSON.stringify(sortThird([5, 6, 9, 4, 8, 3, 2])) ==
      JSON.stringify([2, 6, 9, 4, 8, 3, 5])
  )
  console.assert(
    JSON.stringify(sortThird([5, 6, 3, 4, 8, 9, 2, 1])) ==
      JSON.stringify([2, 6, 3, 4, 8, 9, 5, 1])
  )
}

testSortThird()
