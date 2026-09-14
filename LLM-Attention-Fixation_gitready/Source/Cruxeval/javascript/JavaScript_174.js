function f(lst){
    lst.splice(1, 3, ...lst.slice(1, 4).reverse());
    return lst;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3]),[1, 3, 2]);
}

test();
