function f(text, s, e) {
    let sublist = text.slice(s, e);
    if (!sublist) {
        return -1;
    }
    let minChar = sublist[0];
    let minIndex = 0;
    for (let i = 1; i < sublist.length; i++) {
        if (sublist[i] < minChar) {
            minChar = sublist[i];
            minIndex = i;
        }
    }
    return minIndex;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("happy", 0, 3),1);
}

test();
