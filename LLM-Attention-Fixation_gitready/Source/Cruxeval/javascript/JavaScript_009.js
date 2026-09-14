function f(t){
    for(let i=0; i<t.length; i++){
        if(isNaN(parseInt(t[i]))){
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("#284376598"),false);
}

test();
