function f(array, elem){
    var ind = array.indexOf(elem);
    return ind * 2 + array[array.length - ind - 1] * 3;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-1, 2, 1, -8, 2], 2),-22);
}

test();
