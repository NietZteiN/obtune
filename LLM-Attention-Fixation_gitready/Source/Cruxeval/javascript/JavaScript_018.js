function f(array, elem){
    let k = 0;
    let l = array.slice();
    for (let i of l){
        if (i > elem){
            array.splice(k, 0, elem);
            break;
        }
        k++;
    }
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([5, 4, 3, 2, 1, 0], 3),[3, 5, 4, 3, 2, 1, 0]);
}

test();
