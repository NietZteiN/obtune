function f(s, sep){
    s += sep;
    return s.slice(0, s.lastIndexOf(sep));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("234dsfssdfs333324314", "s"),"234dsfssdfs333324314");
}

test();
