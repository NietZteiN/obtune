function f(nums){
    let count = 0;
    while(nums.length !== 0){
        if(count % 2 === 0){
            nums.pop();
        } else {
            nums.shift();
        }
        count++;
    }
    return nums;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 2, 0, 0, 2, 3]),[]);
}

test();
