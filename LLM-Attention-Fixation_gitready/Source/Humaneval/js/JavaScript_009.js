/* From a given list of integers, generate a list of rolling maximum element found until given moment
  in the sequence.
  >>> rollingMax([1, 2, 3, 2, 3, 4, 2])
  [1, 2, 3, 3, 3, 4, 4]
  */
const rollingMax = (numbers) => {

  var running_max, result = [];
  for (const n of numbers) {
    if (running_max == undefined)
      running_max = n;
    else
      running_max = Math.max(running_max, n);
    result.push(running_max);
  }
  return result;
}

const testRollingMax = () => {
  console.assert(JSON.stringify(rollingMax([])) === JSON.stringify([]))
  console.assert(
    JSON.stringify(rollingMax([1, 2, 3, 4])) === JSON.stringify([1, 2, 3, 4])
  )
  console.assert(
    JSON.stringify(rollingMax([4, 3, 2, 1])) === JSON.stringify([4, 4, 4, 4])
  )
  console.assert(
    JSON.stringify(
      rollingMax([3, 2, 3, 100, 3])) === JSON.stringify([3, 3, 3, 100, 100])
  )
}

testRollingMax()
