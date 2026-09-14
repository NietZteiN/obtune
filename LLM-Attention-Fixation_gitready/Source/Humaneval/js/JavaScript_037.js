/*This function takes a list l and returns a list l' such that
  l' is identical to l in the odd indicies, while its values at the even indicies are equal
  to the values of the even indicies of l, but sorted.
  >>> sortEven([1, 2, 3])
  [1, 2, 3]
  >>> sortEven([5, 6, 3, 4])
  [3, 6, 5, 4]
  */
const sortEven = (l) => {

  var even = l.filter((item, index) => index % 2 == 0);
  even.sort((a, b) => (a - b));
  return l.map((item, index) => (index % 2 == 0 ? even[index / 2] : item));
}

const testSortEven = () => {
  console.assert(JSON.stringify(sortEven([1, 2, 3])) ===
    JSON.stringify([1, 2, 3]))
  console.assert(JSON.stringify(
    sortEven([5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10])) ===
    JSON.stringify([-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123]))
  console.assert(JSON.stringify(
    sortEven([5, 8, -12, 4, 23, 2, 3, 11, 12, -10])) ===
    JSON.stringify([-12, 8, 3, 4, 5, 2, 12, 11, 23, -10]))
}

testSortEven()
