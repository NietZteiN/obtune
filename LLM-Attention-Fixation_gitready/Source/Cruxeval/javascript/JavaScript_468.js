function f(a, b, n){
    let result = m = b;
    for (let i = 0; i < n; i++) {
        if (m) {
            [a, m] = [a.replace(m, ''), null];
            result = m = b;
        }
    }
    return a.split(b).join(result);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("unrndqafi", "c", 2),"unrndqafi");
}

test();
