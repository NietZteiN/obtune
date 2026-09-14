function f(nums){
    return nums[Math.floor(nums.length / 2)];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-1, -3, -5, -7, 0]),-5);
}

test();
