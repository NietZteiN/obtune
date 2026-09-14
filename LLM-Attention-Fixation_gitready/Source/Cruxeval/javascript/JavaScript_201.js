function f(text){
    let chars = [];
    for(let i = 0; i < text.length; i++){
        if (!isNaN(parseInt(text[i]))) {
            chars.push(text[i]);
        }
    }
    return chars.reverse().join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("--4yrw 251-//4 6p"),"641524");
}

test();
