function f(text){
    let new_text = [];
    for(let i = 0; i < text.length; i++){
        if(text[i] == text[i].toUpperCase() && text[i] != text[i].toLowerCase()){
            new_text.splice(Math.floor(new_text.length / 2), 0, text[i]);
        }
    }
    if(new_text.length == 0){
        new_text.push('-');
    }
    return new_text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("String matching is a big part of RexEx library."),"RES");
}

test();
