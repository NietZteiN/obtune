function f(n){
    n = String(n);
    return n.charAt(0) + '.' + n.slice(1).replace(/-/g, '_');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("first-second-third"),"f.irst_second_third");
}

test();
