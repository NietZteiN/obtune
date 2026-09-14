function f(text, search){
    return search.startsWith(text) || false;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("123", "123eenhas0"),true);
}

test();
