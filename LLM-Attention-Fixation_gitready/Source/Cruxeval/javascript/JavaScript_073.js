function f(row){
    return [row.split('1').length - 1, row.split('0').length - 1];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("100010010"),[3, 6]);
}

test();
