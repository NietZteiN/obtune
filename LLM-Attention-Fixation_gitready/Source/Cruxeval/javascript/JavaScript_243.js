function f(text, char){
    return char.toLowerCase() === char && text.toLowerCase() === text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abc", "e"),true);
}

test();
