function f(text, num_digits){
    let width = Math.max(1, num_digits);
    return text.padStart(width, '0');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("19", 5),"00019");
}

test();
