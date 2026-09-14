function f(nums, i){
    nums.splice(i, 1);
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([35, 45, 3, 61, 39, 27, 47], 0),[45, 3, 61, 39, 27, 47]);
}

test();
