function f(nums, rmvalue){
    let res = nums.slice();
    while (res.includes(rmvalue)) {
        let index = res.indexOf(rmvalue);
        let popped = res.splice(index, 1)[0];
        if (popped !== rmvalue) {
            res.push(popped);
        }
    }
    return res;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6, 2, 1, 1, 4, 1], 5),[6, 2, 1, 1, 4, 1]);
}

test();
