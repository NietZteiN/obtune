function f(s, c){
    s = s.split(' ');
    return c + "  " + s.reverse().join("  ");
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hello There", "*"),"*  There  Hello");
}

test();
