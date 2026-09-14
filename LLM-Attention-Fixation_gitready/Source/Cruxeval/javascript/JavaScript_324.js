function f(nums){
    let asc = nums.slice();
    let desc = [];
    let temp = asc.slice();
    temp.reverse();
    desc = temp.slice(0, Math.floor(temp.length / 2));
    return desc.concat(asc).concat(desc);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
