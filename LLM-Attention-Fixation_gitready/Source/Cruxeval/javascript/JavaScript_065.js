function f(nums, index){
    return nums[index] % 42 + nums.splice(index, 1)[0] * 2;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 2, 0, 3, 7], 3),9);
}

test();
