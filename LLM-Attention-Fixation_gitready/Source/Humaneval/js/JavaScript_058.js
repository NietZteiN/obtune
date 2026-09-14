/*Return sorted unique common elements for two lists.
  >>> common([1, 4, 3, 34, 653, 2, 5], [5, 7, 1, 5, 9, 653, 121])
  [1, 5, 653]
  >>> common([5, 3, 2, 8], [3, 2])
  [2, 3]

  */
const common = (l1, l2) => {

  var ret = new Set();
  for (const e1 of l1)
    for (const e2 of l2)
      if (e1 == e2)
        ret.add(e1);
  return [...ret].sort();
}

const testCommon = () => {
  console.assert(
    JSON.stringify(common([1, 4, 3, 34, 653, 2, 5], [5, 7, 1, 5, 9, 653, 121]))
     === JSON.stringify([1, 5, 653])
  )
  console.assert(
    JSON.stringify(common([5, 3, 2, 8], [3, 2]))
     === JSON.stringify([2, 3])
  )
  console.assert(
    JSON.stringify(common([4, 3, 2, 8], [3, 2, 4])) ===
      JSON.stringify([2, 3, 4])
  )
  console.assert(
    JSON.stringify(common([4, 3, 2, 8], [])) === JSON.stringify([])
  )
}

testCommon()
