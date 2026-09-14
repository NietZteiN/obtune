function f(s, l){
    return s.padEnd(l, '=').split('=')[0];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("urecord", 8),"urecord");
}

test();
