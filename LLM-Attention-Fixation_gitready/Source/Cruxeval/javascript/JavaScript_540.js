function f(a){
    let b = a.slice();
    for(let k = 0; k < a.length - 1; k += 2){
        b.splice(k + 1, 0, b[k]);
    }
    b.push(b[0]);
    return b;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([5, 5, 5, 6, 4, 9]),[5, 5, 5, 5, 5, 5, 6, 4, 9, 5]);
}

test();
