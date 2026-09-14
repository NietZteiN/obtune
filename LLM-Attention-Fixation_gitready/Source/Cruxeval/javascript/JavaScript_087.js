function f(nums){
    nums.reverse();
    return nums.map(String).join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-1, 9, 3, 1, -2]),"-2139-1");
}

test();
