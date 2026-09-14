function f(nums, mos) {
    for (let num of mos) {
        nums.splice(nums.indexOf(num), 1);
    }
    nums.sort();
    for (let num of mos) {
        nums.push(num);
    }
    for (let i = 0; i < nums.length - 1; i++) {
        if (nums[i] > nums[i + 1]) {
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 1, 2, 1, 4, 1], [1]),false);
}

test();
