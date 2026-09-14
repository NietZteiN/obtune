function f(array, elem){
    for (let idx = 0; idx < array.length; idx++) {
        if (array[idx] > elem && array[idx - 1] < elem) {
            array.splice(idx, 0, elem);
        }
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 5, 8], 6),[1, 2, 3, 5, 6, 8]);
}

test();
