function f(text){
    let s = text.toLowerCase();
    for(let i = 0; i < s.length; i++){
        if(s[i] === 'x'){
            return 'no';
        }
    }
    return text.toUpperCase() === text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("dEXE"),"no");
}

test();
