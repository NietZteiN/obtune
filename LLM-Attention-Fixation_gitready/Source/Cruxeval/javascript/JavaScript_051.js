function f(num){
    let s = '<'.repeat(10);
    if (num % 2 === 0) {
        return s;
    } else {
        return num - 1;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(21),20);
}

test();
