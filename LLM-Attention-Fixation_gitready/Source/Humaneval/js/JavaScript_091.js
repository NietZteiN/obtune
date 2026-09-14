/*
  You'll be given a string of words, and your task is to count the number
  of boredoms. A boredom is a sentence that starts with the word "I".
  Sentences are delimited by '.', '?' or '!'.
 
  For example:
  >>> isBored("Hello world")
  0
  >>> isBored("The sky is blue. The sun is shining. I love this weather")
  1
  */
const isBored = (S) => {

  let t = 0
  if (S[0] == 'I' && S[1] == ' ') { t = 1 }
  for (let i = 0; i < S.length; i++) {
    if (S[i] == '.' || S[i] == '!' || S[i] == '?') {
      if (S[i + 1] == ' ' && S[i + 2] == 'I' && S[i + 3] == ' ') {
        t++
      }
    }
  }
  return t
}

const testIsBored = () => {
  console.assert(isBored('Hello world') === 0)
  console.assert(isBored('Is the sky blue?') === 0)
  console.assert(isBored('I love It !') === 1)
  console.assert(isBored('bIt') === 0)
  console.assert(
    isBored('I feel good today. I will be productive. will kill It') === 2
  )
  console.assert(isBored('You and I are going for a walk') === 0)
}

testIsBored()
