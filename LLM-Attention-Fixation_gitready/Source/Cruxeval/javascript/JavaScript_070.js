function f(x){
    let a = 0;
    x.split(' ').forEach(i => {
        a += i.padStart(i.length * 2, '0').length;
    });
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("999893767522480"),30);
}

test();
