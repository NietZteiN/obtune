function f(orig){
    let copy = orig;
    copy.push(100);
    orig.pop();
    return copy;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3]),[1, 2, 3]);
}

test();
