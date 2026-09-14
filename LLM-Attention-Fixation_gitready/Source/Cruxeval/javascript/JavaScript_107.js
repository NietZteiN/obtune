function f(text){
    let result = [];
    for(let i = 0; i < text.length; i++){
        if(!text[i].match(/[ -~]/)){
            return false;
        } else if(text[i].match(/[a-zA-Z0-9]/)){
            result.push(text[i].toUpperCase());
        } else {
            result.push(text[i]);
        }
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ua6hajq"),"UA6HAJQ");
}

test();
