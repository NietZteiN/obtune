function f(s, n){
    if (s.length < n) {
        return s;
    } else {
        return s.substring(n);
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("try.", 5),"try.");
}

test();
