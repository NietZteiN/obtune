function f(nums){
    for(let i = nums.length - 1; i >= 0; i -= 3){
        if(nums[i] === 0){
            nums = [];
            return false;
        }
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 0, 1, 2, 1]),false);
}

test();
