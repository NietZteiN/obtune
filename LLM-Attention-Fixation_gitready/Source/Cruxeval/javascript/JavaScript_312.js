function f(s){
    if (/^[a-zA-Z0-9]+$/.test(s)) {
        return "True";
    }
    return "False";
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("777"),"True");
}

test();
