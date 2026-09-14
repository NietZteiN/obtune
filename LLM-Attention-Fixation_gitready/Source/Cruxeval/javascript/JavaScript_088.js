function f(s1, s2){
    if(s2.endsWith(s1)){
        s2 = s2.slice(0, -s1.length);
    }
    return s2;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("he", "hello"),"hello");
}

test();
