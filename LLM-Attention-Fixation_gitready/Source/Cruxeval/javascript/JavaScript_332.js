function f(nums){
    let count = nums.length;
    if (count === 0){
        nums = Array.from({length: parseInt(nums.pop())}, () => 0);
    } else if (count % 2 === 0){
        nums.length = 0;
    } else {
        nums.splice(0, Math.floor(count / 2));
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-6, -2, 1, -3, 0, 1]),[]);
}

test();
