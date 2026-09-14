function f(s1, s2){
    let position = 1;
    let count = 0;
    while (position > 0) {
        position = s1.indexOf(s2, position);
        count += 1;
        position += 1;
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("xinyyexyxx", "xx"),2);
}

test();
