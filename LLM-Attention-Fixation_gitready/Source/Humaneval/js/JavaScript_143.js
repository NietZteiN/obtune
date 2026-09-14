/*
  You are given a string representing a sentence,
  the sentence contains some words separated by a space,
  and you have to return a string that contains the words from the original sentence,
  whose lengths are prime numbers,
  the order of the words in the new string should be the same as the original one.

  Example 1:
      Input: sentence = "This is a test"
      Output: "is"

  Example 2:
      Input: sentence = "lets go for swimming"
      Output: "go for"

  Constraints:
      * 1 <= len(sentence) <= 100
      * sentence contains only letters
  */
const wordsInSentence = (sentence) => {

  let t = sentence.split(/\s/)
  let p = ''
  for (let j = 0; j < t.length; j++) {
    let len = t[j].length;
    let u = 1
    if (len == 1 || len == 0) { continue }
    for (let i = 2; i * i <= len; i++) {
      if (len % i == 0) { u = 0 }
    }
    if (u == 0) { continue }
    if (p == '') { p += t[j] }
    else { p = p + ' ' + t[j] }
  }
  return p
}

const testWordsInSentence = () => {
  console.assert(wordsInSentence('This is a test') === 'is')
  console.assert(wordsInSentence('lets go for swimming') === 'go for')
  console.assert(
    wordsInSentence('there is no place available here') === 'there is no place'
  )
  console.assert(wordsInSentence('Hi I am Hussein') === 'Hi am Hussein')
  console.assert(wordsInSentence('go for it') === 'go for it')
  console.assert(wordsInSentence('here') === '')
  console.assert(wordsInSentence('here is') === 'is')
}

testWordsInSentence()
