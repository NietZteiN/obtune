function f(nums){
    let a = -1;
    let b = nums.slice(1);
    while (a <= b[0]){
        nums.splice(nums.indexOf(b[0]), 1);
        a = 0;
        b = b.slice(1);
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-1, 5, 3, -2, -6, 8, 8]),[-1, -2, -6, 8, 8]);
}

test();
