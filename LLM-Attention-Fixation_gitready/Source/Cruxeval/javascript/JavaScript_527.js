function f(text, value){
    return text.padEnd(value.length, "?");
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("!?", ""),"!?");
}

test();
