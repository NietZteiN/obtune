function f(lst, mode){
    let result = lst.slice();
    if (mode) {
        result.reverse();
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 4], 1),[4, 3, 2, 1]);
}

test();
