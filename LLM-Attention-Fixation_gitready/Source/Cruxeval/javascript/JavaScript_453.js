function f(string, c){
    return string.endsWith(c);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("wrsch)xjmb8", "c"),false);
}

test();
