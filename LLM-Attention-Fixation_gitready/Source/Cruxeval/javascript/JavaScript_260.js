function f(nums, start, k){
    nums.splice(start, k, ...nums.slice(start, start + k).reverse());
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 4, 5, 6], 4, 2),[1, 2, 3, 4, 6, 5]);
}

test();
