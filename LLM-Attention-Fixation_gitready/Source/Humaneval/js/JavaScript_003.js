/* You're given a list of deposit and withdrawal operations on a bank account that starts with
  zero balance. Your task is to detect if at any point the balance of account fallls below zero, and
  at that point function should return true. Otherwise it should return false.
  >>> belowZero([1, 2, 3])
  false
  >>> belowZero([1, 2, -4, 5])
  true
  */
const belowZero = (operations) => {

  var balance = 0;
  for (const op of operations) {
    balance += op;
    if (balance < 0) {
      return true;
    }
  }
  return false;
}

const testBelowZero = () => {
  console.assert(belowZero([]) === false)
  console.assert(belowZero([1, 2, -3, 1, 2, -3]) === false)
  console.assert(belowZero([1, 2, -4, 5, 6]) === true)
  console.assert(belowZero([1, -1, 2, -2, 5, -5, 4, -4]) === false)
  console.assert(belowZero([1, -1, 2, -2, 5, -5, 4, -5]) === true)
  console.assert(belowZero([1, -2, 2, -2, 5, -5, 4, -4]) === true)
}

testBelowZero()
