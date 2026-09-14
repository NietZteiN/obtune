function f(s){
    return s.replace(/\(/g, '[').replace(/\)/g, ']');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("(ac)"),"[ac]");
}

test();
