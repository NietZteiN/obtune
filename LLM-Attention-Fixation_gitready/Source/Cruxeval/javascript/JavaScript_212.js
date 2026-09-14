function f(nums){
    for(let i = 0; i < nums.length - 1; i++){
        nums.reverse();
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, -9, 7, 2, 6, -3, 3]),[1, -9, 7, 2, 6, -3, 3]);
}

test();
