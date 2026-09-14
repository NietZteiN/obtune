function f(text, chars){
    return text.trimEnd(chars);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ha", ""),"ha");
}

test();
