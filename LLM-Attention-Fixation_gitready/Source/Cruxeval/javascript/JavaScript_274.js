function f(nums, target){
    let count = 0;
    for(let n1 of nums){
        for(let n2 of nums){
            count += n1 + n2 === target ? 1 : 0;
        }
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3], 4),3);
}

test();
