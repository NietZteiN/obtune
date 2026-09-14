function f(s1, s2){
    let len = s2.length + s1.length;
    for(let k = 0; k < len; k++){
        s1 += s1[0];
        if(s1.indexOf(s2) >= 0){
            return true;
        }
    }
    return false;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hello", ")"),false);
}

test();
