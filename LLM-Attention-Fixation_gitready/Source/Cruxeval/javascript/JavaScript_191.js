function f(string){
    return string === string.toUpperCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Ohno"),false);
}

test();
