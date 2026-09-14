function f(text){
    return text.split('\n').length;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ncdsdfdaaa0a1cdscsk*XFd"),1);
}

test();
