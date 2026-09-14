function f(array){
    let result = array.slice();
    result.reverse();
    result = result.map(item => item * 2);
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 4, 5]),[10, 8, 6, 4, 2]);
}

test();
