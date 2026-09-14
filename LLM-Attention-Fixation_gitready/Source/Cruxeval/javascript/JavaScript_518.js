function f(text){
    return !text.match(/^\d+$/);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("the speed is -36 miles per hour"),true);
}

test();
