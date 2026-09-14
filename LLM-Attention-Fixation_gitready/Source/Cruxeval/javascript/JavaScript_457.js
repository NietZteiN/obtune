function f(nums){
    let count = Array.from({length: nums.length}, (_, i) => i);
    while(nums.length > 0){
        nums.pop();
        if(count.length > 0){
            count.shift();
        }
    }
    return nums;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 1, 7, 5, 6]),[]);
}

test();
