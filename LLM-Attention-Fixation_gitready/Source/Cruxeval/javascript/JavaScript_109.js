function f(nums, spot, idx){
    nums.splice(spot, 0, idx);
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 0, 1, 1], 0, 9),[9, 1, 0, 1, 1]);
}

test();
