/*
  Write a function which sorts the given list of integers
  in ascending order according to the sum of their digits.
  Note: if there are several items with similar sum of their digits,
  order them based on their index in original list.

  For example:
  >>> orderByPoints([1, 11, -1, -11, -12]) == [-1, -11, 1, -12, 11]
  >>> orderByPoints([]) == []
  */
const orderByPoints = (nums) => {

  let p = nums
  for (let j = p.length - 2; j >= 0; j--) {
    for (let k = 0; k <= j; k++) {
      let m = 0
      let n = 0
      let h = p[k]
      let d = p[k + 1]
      let y = 1
      let u = 1
      if (h < 0) { y = -1; h = -h; }
      if (d < 0) { u = -1; d = -d; }
      while (h >= 10) {
        m += h % 10;
        h = (h - h % 10) / 10;
      }
      m += y * h
      while (d >= 10) {
        n += d % 10;
        d = (d - d % 10) / 10;
      }
      n += u * d
      if (m > n) {
        let tmp = p[k]
        p[k] = p[k + 1]
        p[k + 1] = tmp
      }
    }
  }
  return p
}

const testOrderByPoints = () => {
  console.assert(
    JSON.stringify(orderByPoints([1, 11, -1, -11, -12])) ===
    JSON.stringify([-1, -11, 1, -12, 11])
  )
  console.assert(
    JSON.stringify(
      orderByPoints([
        1234, 423, 463, 145, 2, 423, 423, 53, 6, 37, 3457, 3, 56, 0, 46,
      ])
    ) ===
    JSON.stringify([
      0, 2, 3, 6, 53, 423, 423, 423, 1234, 145, 37, 46, 56, 463, 3457,
    ])
  )
  console.assert(JSON.stringify(orderByPoints([])) === JSON.stringify([]))
  console.assert(
    JSON.stringify(orderByPoints([1, -11, -32, 43, 54, -98, 2, -3])) ===
    JSON.stringify([-3, -32, -98, -11, 1, 2, 43, 54])
  )
  console.assert(
    JSON.stringify(orderByPoints([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])) ===
    JSON.stringify([1, 10, 2, 11, 3, 4, 5, 6, 7, 8, 9])
  )
  console.assert(
    JSON.stringify(orderByPoints([0, 6, 6, -76, -21, 23, 4])) ===
    JSON.stringify([-76, -21, 0, 4, 23, 6, 6])
  )
}

testOrderByPoints()
