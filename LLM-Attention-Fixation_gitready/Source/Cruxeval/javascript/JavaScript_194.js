function f(matr, insert_loc){
    matr.splice(insert_loc, 0, []);
    return matr;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[5, 6, 2, 3], [1, 9, 5, 6]], 0),[[], [5, 6, 2, 3], [1, 9, 5, 6]]);
}

test();
