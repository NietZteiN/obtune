function f(s){
    return s.length === s.split('0').length + s.split('1').length - 2;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("102"),false);
}

test();
