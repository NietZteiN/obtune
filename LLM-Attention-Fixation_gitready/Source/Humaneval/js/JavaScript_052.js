/*Return true if all numbers in the list l are below threshold t.
  >>> belowThreshold([1, 2, 4, 10], 100)
  true
  >>> belowThreshold([1, 20, 4, 10], 5)
  false
  */
const belowThreshold = (l, t) => {

  for (const e of l)
    if (e >= t)
      return false;
  return true;
}

const testBelowThreshold = () => {
  console.assert(belowThreshold([1, 2, 4, 10], 100) === true)
  console.assert(belowThreshold([1, 20, 4, 10], 5) === false)
  console.assert(belowThreshold([1, 20, 4, 10], 21) === true)
  console.assert(belowThreshold([1, 20, 4, 10], 22) === true)
  console.assert(belowThreshold([1, 8, 4, 10], 11) === true)
  console.assert(belowThreshold([1, 8, 4, 10], 10) === false)
}

testBelowThreshold()
