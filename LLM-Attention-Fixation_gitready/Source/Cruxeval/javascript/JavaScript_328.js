function f(array, L){
    if (L <= 0) {
        return array;
    }
    if (array.length < L) {
        array.push(...f(array, L - array.length));
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3], 4),[1, 2, 3, 1, 2, 3]);
}

test();
