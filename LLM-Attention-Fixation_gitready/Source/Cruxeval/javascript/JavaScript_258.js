function f(L, m, start, step){
    L.splice(start, 0, m);
    for(let x = start-1; x > 0; x -= step){
        start -= 1;
        L.splice(start, 0, L.splice(L.lastIndexOf(m)-1, 1)[0]);
    }
    return L;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 7, 9], 3, 3, 2),[1, 2, 7, 3, 9]);
}

test();
