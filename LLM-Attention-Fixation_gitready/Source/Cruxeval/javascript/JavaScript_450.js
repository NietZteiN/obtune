function f(strs){
    strs = strs.split(' ');
    for (let i = 1; i < strs.length; i += 2) {
        strs[i] = strs[i].split('').reverse().join('');
    }
    return strs.join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("K zBK"),"K KBz");
}

test();
