function f(values){
    values.sort((a, b) => a - b);
    return values;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 1, 1, 1]),[1, 1, 1, 1]);
}

test();
