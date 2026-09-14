function f(nums, pop1, pop2){
    nums.splice(pop1 - 1, 1);
    nums.splice(pop2 - 1, 1);
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 5, 2, 3, 6], 2, 4),[1, 2, 3]);
}

test();
