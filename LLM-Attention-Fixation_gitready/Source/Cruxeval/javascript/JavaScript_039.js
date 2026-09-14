function f(array, elem){
    if (array.includes(elem)) {
        return array.indexOf(elem);
    }
    return -1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6, 2, 7, 1], 6),0);
}

test();
