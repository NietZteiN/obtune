function f(text){
    for(let char of text){
        if(char !== ' '){
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("     i"),false);
}

test();
