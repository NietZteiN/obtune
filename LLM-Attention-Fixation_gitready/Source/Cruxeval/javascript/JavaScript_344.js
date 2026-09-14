function f(lst){
    let operation = x => x.reverse();
    let new_list = [...lst];
    new_list.sort((a, b) => a - b);
    operation(new_list);
    return lst;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6, 4, 2, 8, 15]),[6, 4, 2, 8, 15]);
}

test();
