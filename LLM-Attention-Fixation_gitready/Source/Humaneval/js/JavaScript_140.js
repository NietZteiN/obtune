/*
  Given a string text, replace all spaces in it with underscores, 
  and if a string has more than 2 consecutive spaces, 
  then replace all consecutive spaces with - 
  
  fixSpaces("Example") == "Example"
  fixSpaces("Example 1") == "Example_1"
  fixSpaces(" Example 2") == "_Example_2"
  fixSpaces(" Example   3") == "_Example-3"
  */
const fixSpaces = (text) => {

  let t = ''
  let c = 0
  for (let i = 0; i < text.length; i++) {
    if (text[i] == ' ') { c++ }
    else if (c > 0) {
      if (c == 1) { t += '_' }
      if (c == 2) { t += '__' }
      if (c > 2) { t += '-' }
      t += text[i]
      c = 0;
    } else {
      t += text[i]
    }
  }
  if (c == 1) { t += '_' }
  if (c == 2) { t += '__' }
  if (c > 2) { t += '-' }
  return t
}

const testFixSpaces = () => {
  console.assert(fixSpaces('Example') === 'Example')
  console.assert(fixSpaces('Mudasir Hanif ') === 'Mudasir_Hanif_')
  console.assert(
    fixSpaces('Yellow Yellow  Dirty  Fellow') === 'Yellow_Yellow__Dirty__Fellow'
  )
  console.assert(fixSpaces('Exa   mple') === 'Exa-mple')
  console.assert(fixSpaces('   Exa 1 2 2 mple') === '-Exa_1_2_2_mple')
}

testFixSpaces()
