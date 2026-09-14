/*
  Checks if given string is a palindrome
  >>> isPalindrome('')
  true
  >>> isPalindrome('aba')
  true
  >>> isPalindrome('aaaaa')
  true
  >>> isPalindrome('zbcd')
  false
  */
const isPalindrome = (text) => {

  for (let i = 0; i < text.length; i++)
    if (text[i] != text.at(-i-1))
      return false;
  return true;
}

const testIsPalindrome = () => {
  console.assert(isPalindrome('') === true)
  console.assert(isPalindrome('aba') === true)
  console.assert(isPalindrome('aaaaa') === true)
  console.assert(isPalindrome('zbcd') === false)
  console.assert(isPalindrome('xywyx') === true)
  console.assert(isPalindrome('xywyz') === false)
  console.assert(isPalindrome('xywzx') === false)
}

testIsPalindrome()
