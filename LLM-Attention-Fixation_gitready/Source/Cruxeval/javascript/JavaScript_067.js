function f(num1, num2, num3){
    let nums = [num1, num2, num3];
    nums.sort((a, b) => a - b);    
    return `${nums[0]},${nums[1]},${nums[2]}`;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(6, 8, 8),"6,8,8");
}

test();
