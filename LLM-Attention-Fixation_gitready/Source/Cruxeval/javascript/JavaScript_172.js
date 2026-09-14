function f(array){
    for (let i = 0; i < array.length; i++){
        if (array[i] < 0){
            array.splice(i, 1);
            i--;
        }
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
