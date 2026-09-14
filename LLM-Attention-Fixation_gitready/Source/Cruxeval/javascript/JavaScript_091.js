function f(s){
    let d = Array.from(new Set(s.split('')));
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("12ab23xy"),["1", "2", "a", "b", "3", "x", "y"]);
}

test();
