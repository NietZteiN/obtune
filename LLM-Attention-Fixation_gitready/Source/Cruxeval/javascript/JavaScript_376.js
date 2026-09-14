function f(text){
    for(let i = 0; i < text.length; i++){
        if(text.slice(0, i).startsWith("two")){
            return text.slice(i);
        }
    }
    return 'no';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("2two programmers"),"no");
}

test();
