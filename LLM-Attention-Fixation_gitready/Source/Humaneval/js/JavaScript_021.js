/* Given list of numbers (of at least two elements), apply a linear transform to that list,
  such that the smallest number will become 0 and the largest will become 1
  >>> rescaleToUnit([1.0, 2.0, 3.0, 4.0, 5.0])
  [0.0, 0.25, 0.5, 0.75, 1.0]
  */
const rescaleToUnit = (numbers) => {

  var min_number = Math.min(...numbers);
  var max_number = Math.max(...numbers);
  return numbers.map(x => (x - min_number) / (max_number - min_number));
}

const testRescaleToUnit = () => {
  console.assert(
    JSON.stringify(rescaleToUnit([2.0, 49.9])) === JSON.stringify([0.0, 1.0])
  )
  console.assert(
    JSON.stringify(rescaleToUnit([100.0, 49.9])) === JSON.stringify([1.0, 0.0])
  )
  console.assert(
    JSON.stringify(rescaleToUnit([1.0, 2.0, 3.0, 4.0, 5.0])) ===
      JSON.stringify([0.0, 0.25, 0.5, 0.75, 1.0])
  )
  console.assert(
    JSON.stringify(rescaleToUnit([2.0, 1.0, 5.0, 3.0, 4.0])) ===
      JSON.stringify([0.25, 0.0, 1.0, 0.5, 0.75])
  )
  console.assert(
    JSON.stringify(rescaleToUnit([12.0, 11.0, 15.0, 13.0, 14.0])) ===
      JSON.stringify([0.25, 0.0, 1.0, 0.5, 0.75])
  )
}

testRescaleToUnit()
