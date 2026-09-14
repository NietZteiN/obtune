function f(text){
    let a = [];
    for(let i = 0; i < text.length; i++){
        if(!parseInt(text[i]) && text[i] !== '0'){
            a.push(text[i]);
        }
    }
    return a.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("seiq7229 d27"),"seiq d");
}

test();
