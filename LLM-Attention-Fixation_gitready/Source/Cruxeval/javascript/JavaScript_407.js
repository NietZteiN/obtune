function f(s){
    while(s.length > 1){
        s.splice(0, s.length);
        s.push(s.length);
    }
    return s.pop();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6, 1, 2, 3]),0);
}

test();
