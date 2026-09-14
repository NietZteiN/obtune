function f(nums){
    let m = Math.max(...nums);
    for (let i = 0; i < m; i++){
        nums.reverse();
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([43, 0, 4, 77, 5, 2, 0, 9, 77]),[77, 9, 0, 2, 5, 77, 4, 0, 43]);
}

test();
