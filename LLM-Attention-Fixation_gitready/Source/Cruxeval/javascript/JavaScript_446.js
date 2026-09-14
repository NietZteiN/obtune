function f(array){
    let l = array.length;
    if (l % 2 === 0) {
        array = [];
    } else {
        array.reverse();
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
