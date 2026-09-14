function f(array){
    let return_arr = [];
    for (let a of array) {
        return_arr.push([...a]);
    }
    return return_arr;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[1, 2, 3], [], [1, 2, 3]]),[[1, 2, 3], [], [1, 2, 3]]);
}

test();
