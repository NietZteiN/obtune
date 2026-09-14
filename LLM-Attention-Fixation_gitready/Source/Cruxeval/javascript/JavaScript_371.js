function f(nums){
    nums = nums.slice();
    for(let i = nums.length - 1; i >= 0; i--){
        if(nums[i] % 2 !== 0){
            nums.splice(i, 1);
        }
    }
    
    let sum_ = 0;
    for(let num of nums){
        sum_ += num;
    }
    
    return sum_;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([11, 21, 0, 11]),0);
}

test();
