function f(text){
    for(let i = text.length - 1; i > 0; i--){
        if(text[i] !== text[i].toUpperCase()){
            return text.slice(0, i);
        }
    }
    return '';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("SzHjifnzog"),"SzHjifnzo");
}

test();
