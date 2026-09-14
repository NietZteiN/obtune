/*Given an integer. return a tuple that has the number of even and odd digits respectively.

   Example:
      evenOddCount(-12) ==> (1, 1)
      evenOddCount(123) ==> (1, 2)
  */
const evenOddCount = (num) => {

  let o = 0
  let e = 0
  if (num < 0) { num = -num }
  while (num > 0) {
    if (num % 2 == 0) { e++ }
    else { o++ }
    num = (num - num % 10) / 10
  }
  return (e, o)
}

const testEvenOddCount = () => {
  console.assert(JSON.stringify(evenOddCount(7)) === JSON.stringify((0, 1)))
  console.assert(JSON.stringify(evenOddCount(-78)) === JSON.stringify((1, 1)))
  console.assert(JSON.stringify(evenOddCount(3452)) === JSON.stringify((2, 2)))
  console.assert(
    JSON.stringify(evenOddCount(346211)) === JSON.stringify((3, 3))
  )
  console.assert(
    JSON.stringify(evenOddCount(-345821)) === JSON.stringify((3, 3))
  )
  console.assert(JSON.stringify(evenOddCount(-2)) === JSON.stringify((1, 0)))
  console.assert(
    JSON.stringify(evenOddCount(-45347)) === JSON.stringify((2, 3))
  )
  console.assert(JSON.stringify(evenOddCount(0)) === JSON.stringify((1, 0)))
}

testEvenOddCount()
