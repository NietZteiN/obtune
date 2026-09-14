function f(text){
    let result = "";
    for(let i = 0; i < text.length; i++){
        if(i % 2 === 0){
            result += text[i].toUpperCase();
        } else {
            result += text[i];
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("vsnlygltaw"),"VsNlYgLtAw");
}

test();
