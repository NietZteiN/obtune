function f(m){
    m.reverse();
    return m;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-4, 6, 0, 4, -7, 2, -1]),[-1, 2, -7, 4, 0, 6, -4]);
}

test();
