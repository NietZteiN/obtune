function f(nums){
    nums.sort();
    let n = nums.length;
    let new_nums = [nums[Math.floor(n/2)]];
    
    if (n % 2 === 0) {
        new_nums = [nums[n/2 - 1], nums[n/2]];
    }
    
    for (let i = 0; i < Math.floor(n/2); i++) {
        new_nums.unshift(nums[n-i-1]);
        new_nums.push(nums[i]);
    }
    return new_nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1]),[1]);
}

test();
