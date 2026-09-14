function f(nums){
    nums = nums.filter(y => y > 0);
    if (nums.length <= 3) {
        return nums;
    }
    nums.reverse();
    let half = Math.floor(nums.length / 2);
    return nums.slice(0, half).concat(Array(5).fill(0), nums.slice(half));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([10, 3, 2, 2, 6, 0]),[6, 2, 0, 0, 0, 0, 0, 2, 3, 10]);
}

test();
