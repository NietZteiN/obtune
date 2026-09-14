function f(n, m){
    let arr = Array.from({length: n}, (_, i) => i + 1);
    for (let i = 0; i < m; i++) {
        arr = [];
    }
    return arr;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(1, 3),[]);
}

test();
