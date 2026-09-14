function f(array){
    let d = Object.fromEntries(array);
    for (let [key, value] of Object.entries(d)) {
        if (value < 0 || value > 9) {
            return null;
        }
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[8, 5], [8, 2], [5, 3]]),{8: 2, 5: 3});
}

test();
