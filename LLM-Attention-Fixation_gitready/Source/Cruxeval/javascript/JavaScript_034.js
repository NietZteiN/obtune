function f(nums, odd1, odd2){
    while(nums.includes(odd1)){
        nums.splice(nums.indexOf(odd1), 1);
    }
    while(nums.includes(odd2)){
        nums.splice(nums.indexOf(odd2), 1);
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 7, 7, 6, 8, 4, 1, 2, 3, 5, 1, 3, 21, 1, 3], 3, 1),[2, 7, 7, 6, 8, 4, 2, 5, 21]);
}

test();
