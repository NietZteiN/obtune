function f(array, n){
    return array.slice(n);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 0, 1, 2, 2, 2, 2], 4),[2, 2, 2]);
}

test();
