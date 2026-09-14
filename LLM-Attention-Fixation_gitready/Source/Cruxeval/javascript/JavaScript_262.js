function f(nums){
    const score = {0: "F", 1: "E", 2: "D", 3: "C", 4: "B", 5: "A", 6: ""};
    let result = [];
    for (let i = 0; i < nums.length; i++) {
        result.push(score[nums[i]]);
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([4, 5]),"BA");
}

test();
