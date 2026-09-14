function f(text){
    let n = 0;
    for(let char of text){
        if(char === char.toUpperCase() && char !== char.toLowerCase()){
            n += 1;
        }
    }
    return n;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("AAAAAAAAAAAAAAAAAAAA"),20);
}

test();
