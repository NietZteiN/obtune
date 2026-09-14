function f(text, search){
    var result = text.toLowerCase();
    return result.indexOf(search.toLowerCase());
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("car hat", "car"),0);
}

test();
