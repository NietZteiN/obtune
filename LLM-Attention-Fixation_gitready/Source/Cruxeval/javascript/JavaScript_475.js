function f(array, index){
    if (index < 0) {
        index = array.length + index;
    }
    return array[index];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1], 0),1);
}

test();
