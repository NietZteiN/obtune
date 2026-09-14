function f(array, elem){
    array.push(...elem);
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[1, 2, 3], [1, 2], 1], [[1, 2, 3], 3, [2, 1]]),[[1, 2, 3], [1, 2], 1, [1, 2, 3], 3, [2, 1]]);
}

test();
