function f(value, char){
    let total = 0;
    for(let i = 0; i < value.length; i++){
        if(value[i] === char || value[i].toLowerCase() === char){
            total++;
        }
    }
    return total;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("234rtccde", "e"),1);
}

test();
