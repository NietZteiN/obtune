function f(nums){
    let verdict = (x) => x < 2;
    let res = nums.filter(x => x !== 0);
    let result = res.map(x => [x, verdict(x)]);
    if (result.length > 0)
        return result;
    return 'error - no numbers or all zeros!';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 3, 0, 1]),[[3, false], [1, true]]);
}

test();
