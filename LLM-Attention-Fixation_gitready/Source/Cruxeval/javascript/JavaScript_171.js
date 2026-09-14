function f(nums){
    const count = Math.floor(nums.length / 2);
    for (let i = 0; i < count; i++) {
        nums.shift();
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 4, 1, 2, 3]),[1, 2, 3]);
}

test();
