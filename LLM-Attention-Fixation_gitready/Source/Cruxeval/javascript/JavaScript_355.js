function f(text, prefix){
    return text.substring(prefix.length);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("123x John z", "z"),"23x John z");
}

test();
