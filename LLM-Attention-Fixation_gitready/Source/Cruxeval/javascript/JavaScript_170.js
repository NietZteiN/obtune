function f(nums, number){
    return nums.reduce((count, current) => current === number ? count + 1 : count, 0);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([12, 0, 13, 4, 12], 12),2);
}

test();
