/* From a list of integers, remove all elements that occur more than once.
  Keep order of elements left the same as in the input.
  >>> removeDuplicates([1, 2, 3, 2, 4])
  [1, 3, 4]
  */
const removeDuplicates = (numbers) => {

  var dict = new Object();
  for (const num of numbers) {
    if (num in dict) {
      dict[num] += 1;
    } else {
      dict[num] = 1;
    }
  }
  return numbers.filter(x => dict[x] <= 1);
}

const testRemoveDuplicates = () => {
  console.assert(JSON.stringify(removeDuplicates([])) === JSON.stringify([]))
  console.assert(
    JSON.stringify(removeDuplicates([1, 2, 3, 4])) ===
      JSON.stringify([1, 2, 3, 4])
  )
  console.assert(
    JSON.stringify(removeDuplicates([1, 2, 3, 2, 4, 3, 5])) ===
      JSON.stringify([1, 4, 5])
  )
}

testRemoveDuplicates()
