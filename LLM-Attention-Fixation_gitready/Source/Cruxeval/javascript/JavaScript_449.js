function f(x){
    let n = x.length;
    let i = 0;
    while (i < n && !isNaN(x[i])) {
        i++;
    }
    return i === n;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("1"),true);
}

test();
