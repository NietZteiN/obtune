function f(nums){
    let count = nums.length;
    for (let i = count - 1; i > 0; i -= 2) {
        nums.splice(i, 0, nums.shift() + nums.shift());
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-5, 3, -2, -3, -1, 3, 5]),[5, -2, 2, -5]);
}

test();
