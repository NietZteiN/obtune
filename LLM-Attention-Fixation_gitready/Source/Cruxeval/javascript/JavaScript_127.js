function f(text) {
    let s = text.split('\n');
    return s.length;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`145

12fjkjg`),3);
}

test();
