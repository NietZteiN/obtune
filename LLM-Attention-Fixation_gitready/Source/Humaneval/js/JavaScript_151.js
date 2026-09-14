/* Given a list of numbers, return the sum of squares of the numbers
  in the list that are odd. Ignore numbers that are negative or not integers.
  doubleTheDifference([1, 3, 2, 0]) == 1 + 9 + 0 + 0 = 10
  doubleTheDifference([-1, -2, 0]) == 0
  doubleTheDifference([9, -2]) == 81
  doubleTheDifference([0]) == 0
  If the input list is empty, return 0.
  */
const doubleTheDifference = (lst) => {

  let p = 0
  for (let i = 0; i < lst.length; i++) {
    if (lst[i] % 2 == 1 && lst[i] > 0) {
      p += lst[i] * lst[i]
    }
  }
  return p
}

const testDoubleTheDifference = () => {
  console.assert(doubleTheDifference([]) === 0)
  console.assert(doubleTheDifference([5, 4]) === 25)
  console.assert(doubleTheDifference([0.1, 0.2, 0.3]) === 0)
  console.assert(doubleTheDifference([-10, -20, -30]) === 0)
  console.assert(doubleTheDifference([-1, -2, 8]) === 0)
  console.assert(doubleTheDifference([0.2, 3, 5]) === 34)
  let lst = []
  let odd_sum = 0
  for (let i = -99; i < 100; i += 2) {
    if (i % 2 != 0 && i > 0) { odd_sum += i * i }
    lst.push(i)
  }
  console.assert(doubleTheDifference(lst) === odd_sum)
}
