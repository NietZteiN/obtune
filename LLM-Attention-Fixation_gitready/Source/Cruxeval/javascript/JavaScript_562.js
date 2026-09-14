function f(text){
    return text.toUpperCase() === text.toString();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("VTBAEPJSLGAHINS"),true);
}

test();
