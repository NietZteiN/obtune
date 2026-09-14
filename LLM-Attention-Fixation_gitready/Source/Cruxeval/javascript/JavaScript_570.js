function f(array, index, value){
    array.unshift(index + 1);
    if (value >= 1) {
        array.splice(index, 0, value);
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2], 0, 2),[2, 1, 2]);
}

test();
