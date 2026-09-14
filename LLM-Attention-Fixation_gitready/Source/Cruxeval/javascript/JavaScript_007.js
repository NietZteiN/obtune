function f(lst){
    let original = lst.slice();
    while (lst.length > 1) {
        lst.splice(lst.length - 1, 1);
        for (let i = 0; i < lst.length; i++) {
            lst.splice(i, 1);
        }
    }
    lst = original.slice();
    if (lst.length > 0) {
        lst.splice(0, 1);
    }
    return lst;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
