/*You will be given the name of a class (a string) and a list of extensions.
  The extensions are to be used to load additional classes to the class. The
  strength of the extension is as follows: Let CAP be the number of the uppercase
  letters in the extension's name, and let SM be the number of lowercase letters
  in the extension's name, the strength is given by the fraction CAP - SM.
  You should find the strongest extension and return a string in this
  format: ClassName.StrongestExtensionName.
  If there are two or more extensions with the same strength, you should
  choose the one that comes first in the list.
  For example, if you are given "Slices" as the class and a list of the
  extensions: ['SErviNGSliCes', 'Cheese', 'StuFfed'] then you should
  return 'Slices.SErviNGSliCes' since 'SErviNGSliCes' is the strongest extension
  (its strength is -1).
  Example:
  for strongestExtension('my_class', ['AA', 'Be', 'CC']) == 'my_class.AA'
  */
const strongestExtension = (class_name, extensions) => {

  let u = 0
  let s = -Infinity
  for (let i = extensions.length - 1; i >= 0; i--) {
    let y = 0
    for (let j = 0; j < extensions[i].length; j++) {
      let k = extensions[i][j].charCodeAt()
      if (k >= 65 && k <= 90) { y += 1 }
      if (k >= 97 && k <= 122) { y -= 1 }
    }
    if (y >= s) {
      s = y;
      u = i;
    }
  }
  return class_name + '.' + extensions[u]
}

const testStrongestExtension = () => {
  console.assert(
    strongestExtension('Watashi', ['tEN', 'niNE', 'eIGHt8OKe']) ===
    'Watashi.eIGHt8OKe'
  )
  console.assert(
    strongestExtension('Boku123', [
      'nani',
      'NazeDa',
      'YEs.WeCaNe',
      '32145tggg',
    ]) === 'Boku123.YEs.WeCaNe'
  )
  console.assert(
    strongestExtension('__YESIMHERE', [
      't',
      'eMptY',
      'nothing',
      'zeR00',
      'NuLl__',
      '123NoooneB321',
    ]) === '__YESIMHERE.NuLl__'
  )
  console.assert(
    strongestExtension('K', ['Ta', 'TAR', 't234An', 'cosSo']) === 'K.TAR'
  )
  console.assert(
    strongestExtension('__HAHA', ['Tab', '123', '781345', '-_-']) ===
    '__HAHA.123'
  )
  console.assert(
    strongestExtension('YameRore', [
      'HhAas',
      'okIWILL123',
      'WorkOut',
      'Fails',
      '-_-',
    ]) === 'YameRore.okIWILL123'
  )
  console.assert(
    strongestExtension('finNNalLLly', ['Die', 'NowW', 'Wow', 'WoW']) ===
    'finNNalLLly.WoW'
  )
  console.assert(strongestExtension('_', ['Bb', '91245']) === '_.Bb')
  console.assert(strongestExtension('Sp', ['671235', 'Bb']) === 'Sp.671235')
}

testStrongestExtension()
