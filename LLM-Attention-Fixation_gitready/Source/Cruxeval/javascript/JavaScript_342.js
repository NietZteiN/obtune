function f(text){
    return text.split('-').length - 1 === text.length;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("---123-4"),false);
}

test();
