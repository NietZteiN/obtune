/*Create a function which takes a string representing a file's name, and returns
  'Yes' if the the file's name is valid, and returns 'No' otherwise.
  A file's name is considered to be valid if and only if all the following conditions 
  are met:
  - There should not be more than three digits ('0'-'9') in the file's name.
  - The file's name contains exactly one dot '.'
  - The substring before the dot should not be empty, and it starts with a letter from 
  the latin alphapet ('a'-'z' and 'A'-'Z').
  - The substring after the dot should be one of these: ['txt', 'exe', 'dll']
  Examples:
  fileNameCheck("example.txt") # => 'Yes'
  fileNameCheck("1example.dll") # => 'No' (the name should start with a latin alphapet letter)
  */
const fileNameCheck = (file_name) => {

  let t = file_name.split(/\./)
  if (t.length != 2) { return 'No' }
  if (t[1] != 'txt' && t[1] != 'dll' && t[1] != 'exe') { return 'No' }
  if (t[0] == '') { return 'No' }
  let a = t[0][0].charCodeAt()
  if (!((a >= 65 && a <= 90) || (a >= 97 && a <= 122))) { return 'No' }
  let y = 0
  for (let i = 1; i < t[0].length; i++) {
    if (t[0][i].charCodeAt() >= 48 && t[0][i].charCodeAt() <= 57) { y++ }
    if (y > 3) { return 'No' }
  }
  return 'Yes'
}

const testFileNameCheck = () => {
  console.assert(fileNameCheck('example.txt') === 'Yes')
  console.assert(fileNameCheck('1example.dll') === 'No')
  console.assert(fileNameCheck('s1sdf3.asd') === 'No')
  console.assert(fileNameCheck('K.dll') === 'Yes')
  console.assert(fileNameCheck('MY16FILE3.exe') === 'Yes')
  console.assert(fileNameCheck('His12FILE94.exe') === 'No')
  console.assert(fileNameCheck('_Y.txt') === 'No')
  console.assert(fileNameCheck('?aREYA.exe') === 'No')
  console.assert(fileNameCheck('/this_is_valid.dll') === 'No')
  console.assert(fileNameCheck('this_is_valid.wow') === 'No')
  console.assert(fileNameCheck('this_is_valid.txt') === 'Yes')
  console.assert(fileNameCheck('this_is_valid.txtexe') === 'No')
  console.assert(fileNameCheck('#this2_i4s_5valid.ten') === 'No')
  console.assert(fileNameCheck('@this1_is6_valid.exe') === 'No')
  console.assert(fileNameCheck('this_is_12valid.6exe4.txt') === 'No')
  console.assert(fileNameCheck('all.exe.txt') === 'No')
  console.assert(fileNameCheck('I563_No.exe') === 'Yes')
  console.assert(fileNameCheck('Is3youfault.txt') === 'Yes')
  console.assert(fileNameCheck('no_one#knows.dll') === 'Yes')
  console.assert(fileNameCheck('1I563_Yes3.exe') === 'No')
  console.assert(fileNameCheck('I563_Yes3.txtt') === 'No')
  console.assert(fileNameCheck('final..txt') === 'No')
  console.assert(fileNameCheck('final132') === 'No')
  console.assert(fileNameCheck('_f4indsartal132.') === 'No')
  console.assert(fileNameCheck('.txt') === 'No')
  console.assert(fileNameCheck('s.') === 'No')
}

testFileNameCheck()
