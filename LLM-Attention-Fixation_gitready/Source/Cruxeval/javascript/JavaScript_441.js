function f(base, k, v){
    base[k] = v;
    return base;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({37: "forty-five"}, "23", "what?"),{37: "forty-five", "23": "what?"});
}

test();
