function f(text){
    for(let i = 0; i < text.length; i++){
        if(isNaN(parseInt(text[i]))){
            return false;
        }
    }
    return Boolean(text);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("99"),true);
}

test();
