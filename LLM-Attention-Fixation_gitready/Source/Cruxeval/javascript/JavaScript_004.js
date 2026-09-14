function f(array){
    let s = ' ';
    s += array.join('');
    return s;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([" ", "  ", "    ", "   "]),"           ");
}

test();
