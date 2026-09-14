function f(arr){
    return arr.slice().reverse();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 0, 1, 9999, 3, -5]),[-5, 3, 9999, 1, 0, 2]);
}

test();
