function f(d) {
    let result = new Array(Object.keys(d).length).fill(null);
    let a = 0;
    let b = 0;
    while (Object.keys(d).length > 0) {
        result[a] = Object.entries(d).splice(a == b ? a : b, 1)[0];
        a = b;
        b = (b + 1) % result.length;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),[]);
}

test();
