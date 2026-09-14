function f(text){
    try {
        return text.match(/^[a-zA-Z]+$/) != null;
    } catch (error) {
        return false;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("x"),true);
}

test();
