function f(nums, target){
    let lows = [];
    let higgs = [];
    nums.forEach(i => {
        if (i < target) {
            lows.push(i);
        } else {
            higgs.push(i);
        }
    });
    lows.length = 0;
    return [lows, higgs];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([12, 516, 5, 2, 3, 214, 51], 5),[[], [12, 516, 5, 214, 51]]);
}

test();
