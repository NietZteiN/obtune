function f(array){
    let n = array.pop();
    array.push(n, n);
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 1, 2, 2]),[1, 1, 2, 2, 2]);
}

test();
