function f(text, count){
    for(let i = 0; i < count; i++){
        text = text.split('').reverse().join('');
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("439m2670hlsw", 3),"wslh0762m934");
}

test();
