function f(li){
    return li.map(i => li.filter(item => item === i).length);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["k", "x", "c", "x", "x", "b", "l", "f", "r", "n", "g"]),[1, 3, 1, 3, 3, 1, 1, 1, 1, 1, 1]);
}

test();
