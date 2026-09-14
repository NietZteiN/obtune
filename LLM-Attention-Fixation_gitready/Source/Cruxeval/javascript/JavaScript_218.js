function f(string, sep){
    let cnt = string.split(sep).length - 1;
    return (string + sep).repeat(cnt).split('').reverse().join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("caabcfcabfc", "ab"),"bacfbacfcbaacbacfbacfcbaac");
}

test();
