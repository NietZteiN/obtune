function f(nums){
    let copy = Object.assign({}, nums);
    let newDict = {};
    for (let k in copy) {
        newDict[k] = copy[k].length;
    }
    return newDict;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),{});
}

test();
