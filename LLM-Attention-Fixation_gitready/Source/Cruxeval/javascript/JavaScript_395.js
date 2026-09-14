function f(s){
    for(let i = 0; i < s.length; i++){
        if(!isNaN(parseInt(s[i]))){
            return i + (s[i] === '0' ? 1 : 0);
        } else if(s[i] === '0'){
            return -1;
        }
    }
    return -1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("11"),0);
}

test();
