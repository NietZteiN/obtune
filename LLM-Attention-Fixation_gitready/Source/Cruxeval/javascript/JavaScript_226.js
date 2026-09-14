function f(nums){
    let result = [];
    for(let i = 0; i < nums.length; i++){
        result.push(nums[i]);
        if(nums[i] % 3 === 0){
            result.push(nums[i]);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 3]),[1, 3, 3]);
}

test();
