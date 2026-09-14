function f(xs){
    let new_x = xs[0] - 1;
    xs.shift();
    while (new_x <= xs[0]){
        xs.shift();
        new_x -= 1;
    }
    xs.unshift(new_x);
    return xs;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6, 3, 4, 1, 2, 3, 5]),[5, 3, 4, 1, 2, 3, 5]);
}

test();
