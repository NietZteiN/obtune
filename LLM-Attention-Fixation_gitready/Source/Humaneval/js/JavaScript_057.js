/*Return true is list elements are monotonically increasing or decreasing.
  >>> monotonic([1, 2, 4, 20])
  true
  >>> monotonic([1, 20, 4, 10])
  false
  >>> monotonic([4, 1, 0, -10])
  true
  */
const monotonic = (l) => {

  var sort1 = [...l].sort((a, b) => a - b);
  var sort2 = [...l].sort((a, b) => b - a);
  if (JSON.stringify(l) === JSON.stringify(sort1) ||
      JSON.stringify(l) === JSON.stringify(sort2))
    return true;
  return false;
}

const testMonotonic = () => {
  console.assert(monotonic([1, 2, 4, 10]) === true)
  console.assert(monotonic([1, 2, 4, 20]) === true)
  console.assert(monotonic([1, 20, 4, 10]) === false)
  console.assert(monotonic([4, 1, 0, -10]) === true)
  console.assert(monotonic([4, 1, 1, 0]) === true)
  console.assert(monotonic([1, 2, 3, 2, 5, 60]) === false)
  console.assert(monotonic([1, 2, 3, 4, 5, 60]) === true)
  console.assert(monotonic([9, 9, 9, 9]) === true)
}

testMonotonic()
