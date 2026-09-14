function f(lst){
    lst.splice(0, lst.length);
    for (let i of lst) {
        if (i === 3) {
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 0]),true);
}

test();
