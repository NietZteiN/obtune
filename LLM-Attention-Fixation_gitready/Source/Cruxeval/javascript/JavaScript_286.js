function f(array, x, i){
    if (i < -array.length || i > array.length - 1) {
        return 'no';
    }
    let temp = array[i];
    array[i] = x;
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11, 4),[1, 2, 3, 4, 11, 6, 7, 8, 9, 10]);
}

test();
