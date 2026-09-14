/*
  returns encoded string by cycling groups of three characters.
  */
const encodeCyclic = (s) => {
  var groups = [], groups2 = [];
  for (let i = 0; i < Math.floor((s.length + 2) / 3); i++) {
    groups.push(s.slice(3 * i, Math.min((3 * i + 3), s.length)));
  }
  for (const group of groups) {
    if (group.length == 3)
      groups2.push(group.slice(1) + group[0]);
    else
      groups2.push(group);
  }
  return groups2.join('');
}

/*
  takes as input string encoded with encode_cyclic function. Returns decoded string.
  */
const decodeCyclic = (s) => {

  return encodeCyclic(encodeCyclic(s));
}

const testDecodeCyclic = () => {
  const letters = new Array(26)
    .fill(null)
    .map((v, i) => String.fromCharCode(97 + i));

  for (let i = 0; i < 100; i++) {
    let str = new Array(Math.floor(Math.random() * 20)).fill(null);
    str = str.map(item => letters[Math.floor(Math.random() * letters.length)]).join('');
    let encoded_str = encodeCyclic(str);
    console.assert(decodeCyclic(encoded_str) === str);
  }
}

testDecodeCyclic()
