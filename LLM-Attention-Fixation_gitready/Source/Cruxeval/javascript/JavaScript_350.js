function f(d){
    let size = Object.keys(d).length;
    let v = new Array(size).fill(0);
    if (size === 0) {
        return v;
    }
    let i = 0;
    for (let e of Object.values(d)) {
        v[i] = e;
        i++;
    }
    return v;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"a": 1, "b": 2, "c": 3}),[1, 2, 3]);
}

test();
