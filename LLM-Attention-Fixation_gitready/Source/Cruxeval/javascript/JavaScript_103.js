function f(s){
    return s.split('').map(c => c.toLowerCase()).join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abcDEFGhIJ"),"abcdefghij");
}

test();
