function f(nums){
    nums.length = 0;
    for (let num of nums) {
        nums.push(num * 2);
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([4, 3, 2, 1, 2, -1, 4, 2]),[]);
}

test();
