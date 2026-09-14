function f(text){
    let counter = 0;
    for(let i = 0; i < text.length; i++){
        if(text[i].match(/[a-zA-Z]/)){
            counter++;
        }
    }
    return counter;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("l000*"),1);
}

test();
