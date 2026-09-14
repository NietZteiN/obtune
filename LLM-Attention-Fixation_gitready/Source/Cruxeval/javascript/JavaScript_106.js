function f(nums){
    let count = nums.length;
    for(let i = 0; i < count; i++){
        nums.splice(i, 0, nums[i]*2);
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 8, -2, 9, 3, 3]),[4, 4, 4, 4, 4, 4, 2, 8, -2, 9, 3, 3]);
}

test();
