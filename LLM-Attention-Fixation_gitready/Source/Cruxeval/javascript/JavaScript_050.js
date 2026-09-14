function f(lst){
    lst.splice(0, lst.length);
    lst.push(...Array(lst.length + 1).fill(1));
    return lst;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["a", "c", "v"]),[1]);
}

test();
