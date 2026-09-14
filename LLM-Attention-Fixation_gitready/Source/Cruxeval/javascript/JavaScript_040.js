function f(text){
    return text.padEnd(text.length + 1, "#");
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("the cow goes moo"),"the cow goes moo#");
}

test();
