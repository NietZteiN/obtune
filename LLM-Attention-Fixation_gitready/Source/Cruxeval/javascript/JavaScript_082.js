function f(a, b, c, d){
    return a && b || c && d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("CJU", "BFS", "WBYDZPVES", "Y"),"BFS");
}

test();
