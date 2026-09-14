function f(array){
    let prev = array[0];
    let newArray = array.slice();
    for (let i = 1; i < array.length; i++) {
        if (prev !== array[i]) {
            newArray[i] = array[i];
        } else {
            newArray.splice(i, 1);
        }
        prev = array[i];
    }
    return newArray;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3]),[1, 2, 3]);
}

test();
