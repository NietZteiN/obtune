function f(text){
    let number = 0;
    for(let i = 0; i < text.length; i++){
        if(!isNaN(text[i])){
            number += 1;
        }
    }
    return number;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Thisisastring"),0);
}

test();
