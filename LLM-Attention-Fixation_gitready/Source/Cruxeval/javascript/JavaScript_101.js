function f(array, i_num, elem){
    array.splice(i_num, 0, elem);
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-4, 1, 0], 1, 4),[-4, 4, 1, 0]);
}

test();
