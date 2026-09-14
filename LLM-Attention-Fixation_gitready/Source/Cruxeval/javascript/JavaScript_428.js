function f(nums){
    for(let i = 0; i < nums.length; i++){
        if(i % 2 === 0){
            nums.push(nums[i] * nums[i + 1]);
        }
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
