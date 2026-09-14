function f(nums, idx, added){
    nums.splice(idx, 0, added);
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 2, 2, 3, 3], 2, 3),[2, 2, 3, 2, 3, 3]);
}

test();
