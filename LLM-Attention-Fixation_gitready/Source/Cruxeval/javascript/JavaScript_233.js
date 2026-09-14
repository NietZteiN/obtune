function f(xs){
    for(let idx = -xs.length; idx < 0; idx++){
        xs.unshift(xs.pop());
    }
    return xs;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3]),[1, 2, 3]);
}

test();
