function f(text) {
    if (/[a-zA-Z]/.test(text) && text === text.toLowerCase()) {
        return true;
    }
    return false;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("54882"),false);
}

test();
