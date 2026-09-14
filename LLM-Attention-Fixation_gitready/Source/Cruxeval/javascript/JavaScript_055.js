function f(array){
    let array_2 = [];
    for (let i of array) {
        if (i > 0) {
            array_2.push(i);
        }
    }
    array_2.sort((a, b) => b - a);
    return array_2;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([4, 8, 17, 89, 43, 14]),[89, 43, 17, 14, 8, 4]);
}

test();
