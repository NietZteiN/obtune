function f(base_list, nums){
    base_list.push(...nums);
    let res = [...base_list];
    for (let i = -nums.length; i < 0; i++) {
        res.push(res[res.length + i]);
    }
    return res;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([9, 7, 5, 3, 1], [2, 4, 6, 8, 0]),[9, 7, 5, 3, 1, 2, 4, 6, 8, 0, 2, 6, 0, 6, 6]);
}

test();
