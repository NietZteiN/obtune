function f(ls){
    return ls.reduce((acc, item) => ({ ...acc, [item]: 0 }), {});
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["x", "u", "w", "j", "3", "6"]),{"x": 0, "u": 0, "w": 0, "j": 0, "3": 0, "6": 0});
}

test();
