function f(sentence){
    for(let i = 0; i < sentence.length; i++){
        if (!sentence[i].match(/[ -~]/)){
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("1z1z1"),true);
}

test();
