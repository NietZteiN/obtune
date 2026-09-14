function f(s, n){
    return s.toLowerCase() === n.toLowerCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("daaX", "daaX"),true);
}

test();
