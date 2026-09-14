function f(s){
    return s.trimRight().split('').reverse().join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ab        "),"ba");
}

test();
