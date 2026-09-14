function f(text, lower, upper){
    return text.substring(lower, upper).split('').every(char => char.charCodeAt(0) < 128);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("=xtanp|sugv?z", 3, 6),true);
}

test();
