function f(s){
    let arr = s.trim().split('');
    arr.reverse();
    return arr.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("   OOP   "),"POO");
}

test();
