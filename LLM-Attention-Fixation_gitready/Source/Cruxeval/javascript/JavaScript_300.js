function f(nums){
    let count = 1;
    for (let i = count; i < nums.length - 1; i += 2) {
        nums[i] = Math.max(nums[i], nums[count-1]);
        count++;
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3]),[1, 2, 3]);
}

test();
