function f(text) {
    let d = {};
    for (let char of text.replace(/-/g, '').toLowerCase()) {
        d[char] = (char in d) ? d[char] + 1 : 1;
    }
    let sortedEntries = Object.entries(d).sort((a, b) => a[1] - b[1]);
    return sortedEntries.map(entry => entry[1]);
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("x--y-z-5-C"),[1, 1, 1, 1, 1]);
}

test();
