function f(cat){
    let digits = 0;
    for(let i = 0; i < cat.length; i++){
        if(!isNaN(parseInt(cat[i]))){
            digits += 1;
        }
    }
    return digits;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("C24Bxxx982ab"),5);
}

test();
