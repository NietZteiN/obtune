function f(array, lst){
    array.push(...lst);
    const evenNumbers = array.filter(e => e % 2 === 0);
    return array.filter(e => e >= 10);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([2, 15], [15, 1]),[15, 15]);
}

test();
