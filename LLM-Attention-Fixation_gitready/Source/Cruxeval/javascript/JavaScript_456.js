function f(s, tab){
    return s.replace(/\t/g, ' '.repeat(tab));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Join us in Hungary", 4),"Join us in Hungary");
}

test();
