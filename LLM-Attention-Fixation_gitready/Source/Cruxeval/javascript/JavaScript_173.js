function f(list_x){
    let item_count = list_x.length;
    let new_list = [];
    for (let i = 0; i < item_count; i++) {
        new_list.push(list_x.pop());
    }
    return new_list;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([5, 8, 6, 8, 4]),[4, 8, 6, 8, 5]);
}

test();
