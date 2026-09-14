function f(array){
    let new_array = array.slice();
    new_array.reverse();
    return new_array.map(x => x*x);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 1]),[1, 4, 1]);
}

test();
