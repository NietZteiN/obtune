function f(text){
    let new_text = text.split('');
    for(let i=0; i<new_text.length; i++){
        if(Number.isInteger(parseInt(new_text[i]))){
            new_text[i] = new_text[i] === '0' ? '.' : new_text[i] === '1' ? '0' : new_text[i];
        }
    }
    return new_text.join('').replaceAll('.', '0');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("697 this is the ultimate 7 address to attack"),"697 this is the ultimate 7 address to attack");
}

test();
