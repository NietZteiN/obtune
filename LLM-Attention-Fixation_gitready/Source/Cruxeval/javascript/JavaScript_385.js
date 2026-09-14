function f(lst){
    let i = 0;
    let new_list = [];
    while (i < lst.length) {
        if (lst.slice(i+1).includes(lst[i])) {
            new_list.push(lst[i]);
            if (new_list.length === 3) {
                return new_list;
            }
        }
        i++;
    }
    return new_list;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 2, 1, 2, 6, 2, 6, 3, 0]),[0, 2, 2]);
}

test();
