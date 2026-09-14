function f(nums){
    for(let i = nums.length-1; i >= 0; i--){
        if(nums[i] % 2 === 1){
            nums.splice(i+1, 0, nums[i]);
        }
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 3, 4, 6, -2]),[2, 3, 3, 4, 6, -2]);
}

test();
