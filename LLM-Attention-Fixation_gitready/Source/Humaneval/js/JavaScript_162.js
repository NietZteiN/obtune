/*
  Given a string 'text', return its md5 hash equivalent string.
  If 'text' is an empty string, return null.

  >>> stringToMd5('Hello world') == '3e25960a79dbc69b674cd4ec67a72c62'
  */
const stringToMd5 = (text) => {

  if (text == '') { return null }
  var md5 = require('js-md5')
  return md5(text)
}

const testStringToMd5 = () => {
  console.assert(
    stringToMd5('Hello world') === '3e25960a79dbc69b674cd4ec67a72c62'
  )
  console.assert(stringToMd5('') === null)
  console.assert(stringToMd5('A B C') === '0ef78513b0cb8cef12743f5aeb35f888')
  console.assert(stringToMd5('password') === '5f4dcc3b5aa765d61d8327deb882cf99')
}

testStringToMd5()
