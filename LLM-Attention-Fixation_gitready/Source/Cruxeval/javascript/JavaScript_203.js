function f(d){
    d = {};
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"a": "3", "b": "-1", "c": "Dum"}),{});
}

test();
