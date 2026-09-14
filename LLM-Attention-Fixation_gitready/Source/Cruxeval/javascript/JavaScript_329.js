function f(text){
    for(let i = 0; i < text.length; i++){
        if(text[i] === text[i].toUpperCase() && text[i-1].toLowerCase() === text[i-1]){
            return true;
        }
    }
    return false;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("jh54kkk6"),true);
}

test();
