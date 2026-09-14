function f(a){
    if (a.length >= 2 && a[0] > 0 && a[1] > 0) {
        a.reverse();
        return a;
    }
    a.push(0);
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[0]);
}

test();
