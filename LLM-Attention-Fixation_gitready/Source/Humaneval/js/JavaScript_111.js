/*Given a string representing a space separated lowercase letters, return a dictionary
  of the letter with the most repetition and containing the corresponding count.
  If several letters have the same occurrence, return all of them.
  
  Example:
  histogram('a b c') == {'a': 1, 'b': 1, 'c': 1}
  histogram('a b b a') == {'a': 2, 'b': 2}
  histogram('a b c a b') == {'a': 2, 'b': 2}
  histogram('b b b b a') == {'b': 4}
  histogram('') == {}

  */
const histogram = (test) => {

  let d = {}
  let t = test.split(/\s/)
  if (test == '') { t = [] }
  for (m in t) {
    if (t[m] in d) {
      d[t[m]]++
    }
    else {
      d[t[m]] = 1
    }
  }
  s = Object.keys(d).sort(function (a, b) { return - d[a] + d[b]; });
  if (s.length == 0) { return {} }
  let g = d[s[0]]
  let l = {}
  for (let ss=0; ss<s.length; ss++) {
    if (d[s[ss]] == g) {
      l[s[ss]] = d[s[ss]]
    }
  }
  return l
}

const testHistogram = () => {
  console.assert(
    JSON.stringify(histogram('a b b a')) === JSON.stringify({ a: 2, b: 2 })
  )
  console.assert(
    JSON.stringify(histogram('a b c a b')) === JSON.stringify({ a: 2, b: 2 })
  )
  console.assert(
    JSON.stringify(histogram('a b c d g')) ===
    JSON.stringify({ a: 1, b: 1, c: 1, d: 1, g: 1 })
  )
  console.assert(
    JSON.stringify(histogram('r t g')) === JSON.stringify({ r: 1, t: 1, g: 1 })
  )
  console.assert(
    JSON.stringify(histogram('b b b b a')) === JSON.stringify({ b: 4 })
  )
  console.assert(
    JSON.stringify(histogram('r t g')) === JSON.stringify({ r: 1, t: 1, g: 1 })
  )
  console.assert(JSON.stringify(histogram('')) === JSON.stringify({}))
  console.assert(JSON.stringify(histogram('a')) === JSON.stringify({ a: 1 }))
}

testHistogram()
