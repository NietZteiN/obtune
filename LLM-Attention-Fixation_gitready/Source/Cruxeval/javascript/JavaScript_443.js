function f(text){
    for(let i=0; i<text.length; i++){
        if(text[i] === ' '){
            text = text.trimLeft();
        }else{
            text = text.replace('cd', text[i]);
        }
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("lorem ipsum"),"lorem ipsum");
}

test();
