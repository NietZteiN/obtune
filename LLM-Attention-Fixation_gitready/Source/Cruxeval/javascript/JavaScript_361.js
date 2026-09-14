function f(text){
    return text.split(':')[0].split('#').length - 1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("#! : #!"),1);
}

test();
