function f(text){
    let count = text.length;
    for(let i = -count+1; i < 0; i++){
        text = text + text[text.length + i];
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("wlace A"),"wlace Alc l  ");
}

test();
