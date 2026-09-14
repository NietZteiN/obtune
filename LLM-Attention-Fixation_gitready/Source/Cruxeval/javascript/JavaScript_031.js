function f(string){
    let upper = 0;
    for(let i = 0; i < string.length; i++){
        if(string[i] === string[i].toUpperCase()){
            upper += 1;
        }
    }
    return upper * (upper % 2 === 0 ? 2 : 1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("PoIOarTvpoead"),8);
}

test();
