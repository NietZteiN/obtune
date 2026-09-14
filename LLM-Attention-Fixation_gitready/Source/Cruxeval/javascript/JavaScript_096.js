function f(text){
    return !text.split('').some(c => c.toUpperCase() === c);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("lunabotics"),true);
}

test();
