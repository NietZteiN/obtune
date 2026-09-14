function f(arr){
    arr = Array.from(arr);
    arr.length = 0;
    arr.push('1', '2', '3', '4');
    return arr.join(',');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 1, 2, 3, 4]),"1,2,3,4");
}

test();
