/*
  returns encoded string by shifting every character by 5 in the alphabet.
  */
const encodeShift = (s) => {
  return s.split("").map(ch => String.fromCharCode(
    ((ch.charCodeAt(0) + 5 - "a".charCodeAt(0)) % 26) + "a".charCodeAt(0)
  )).join("");
}

/*
  takes as input string encoded with encode_shift function. Returns decoded string.
  */
const decodeShift = (s) => {

  return s.split("").map(ch => String.fromCharCode(
    ((ch.charCodeAt(0) - 5 + 26 - "a".charCodeAt(0)) % 26) + "a".charCodeAt(0)
  )).join("");
}

const testDecodeShift = () => {
    const letters = new Array(26)
    .fill(null)
    .map((v, i) => String.fromCharCode(97 + i))

    for (let i = 0; i < 100; i++) {
      let str = new Array(Math.floor(Math.random() * 20)).fill(null);
      str = str.map(item => letters[Math.floor(Math.random() * letters.length)]).join('');
      let encoded_str = encodeShift(str)
      console.assert(decodeShift(encoded_str) === str)
    }

}

testDecodeShift()
