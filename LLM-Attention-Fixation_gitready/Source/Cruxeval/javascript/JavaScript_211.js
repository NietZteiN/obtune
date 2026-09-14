function f(s){
    let count = 0;
    for(let i = 0; i < s.length; i++){
        if(s.lastIndexOf(s[i]) !== s.indexOf(s[i])){
            count++;
        }
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abca dea ead"),10);
}

test();
