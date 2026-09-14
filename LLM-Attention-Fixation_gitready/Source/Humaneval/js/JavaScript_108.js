/*
  Write a function countNums which takes an array of integers and returns
  the number of elements which has a sum of digits > 0.
  If a number is negative, then its first signed digit will be negative:
  e.g. -123 has signed digits -1, 2, and 3.
  >>> countNums([]) == 0
  >>> countNums([-1, 11, -11]) == 1
  >>> countNums([1, 1, 2]) == 3
  */
const countNums = (arr) => {

  let p = 0
  for (let i = 0; i < arr.length; i++) {
    let h = arr[i]
    if (h > 0) {
      p++;
      continue;
    }
    let k = 0
    h = -h
    while (h >= 10) {
      k += h % 10;
      h = (h - h % 10) / 10;
    }
    k -= h;
    if (k > 0) { p++ }
  }
  return p
}

const testCountNums = () => {
  console.assert(countNums([]) === 0)
  console.assert(countNums([-1, -2, 0]) === 0)
  console.assert(countNums([1, 1, 2, -2, 3, 4, 5]) === 6)
  console.assert(countNums([1, 6, 9, -6, 0, 1, 5]) === 5)
  console.assert(countNums([1, 100, 98, -7, 1, -1]) === 4)
  console.assert(countNums([12, 23, 34, -45, -56, 0]) === 5)
  console.assert(countNums([-0, 1 ** 0]) === 1)
  console.assert(countNums([1]) === 1)
}

testCountNums()
