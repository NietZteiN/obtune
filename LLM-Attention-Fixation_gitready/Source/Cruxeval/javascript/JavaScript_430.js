function f(arr1, arr2){
    let new_arr = arr1.slice();
    new_arr.push(...arr2);
    return new_arr;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([5, 1, 3, 7, 8], ["", 0, -1, []]),[5, 1, 3, 7, 8, "", 0, -1, []]);
}

test();
