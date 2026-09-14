function f(a, b){
    a.sort((x, y) => x - y);
    b.sort((x, y) => y - x);
    return a.concat(b);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([666], []),[666]);
}

test();
