function f(text){
    return text.indexOf(",");
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("There are, no, commas, in this text"),9);
}

test();
