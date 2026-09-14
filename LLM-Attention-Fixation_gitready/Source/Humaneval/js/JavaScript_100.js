/*
  Given a positive integer n, you have to make a pile of n levels of stones.
  The first level has n stones.
  The number of stones in the next level is:
      - the next odd number if n is odd.
      - the next even number if n is even.
  Return the number of stones in each level in a list, where element at index
  i represents the number of stones in the level (i+1).

  Examples:
  >>> makeAPile(3)
  [3, 5, 7]
  */
const makeAPile = (n) => {

  let t = []
  for (let i = n; i < n * 3; i += 2) {
    t.push(i)
  }
  return t
}

const testMakeAPile = () => {
  console.assert(JSON.stringify(makeAPile(3)) === JSON.stringify([3, 5, 7]))
  console.assert(JSON.stringify(makeAPile(4)) === JSON.stringify([4, 6, 8, 10]))
  console.assert(
    JSON.stringify(makeAPile(5)) === JSON.stringify([5, 7, 9, 11, 13])
  )
  console.assert(
    JSON.stringify(makeAPile(6)) === JSON.stringify([6, 8, 10, 12, 14, 16])
  )
  console.assert(
    JSON.stringify(makeAPile(8)) ===
    JSON.stringify([8, 10, 12, 14, 16, 18, 20, 22])
  )
}

testMakeAPile()
