function f(nums, pos, value){
    nums.splice(pos, 0, value);
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 1, 2], 2, 0),[3, 1, 0, 2]);
}

test();
