function f(letters){
    let count = 0;
    for(let l of letters){
        if (!isNaN(parseInt(l, 10))){
            count += 1;
        }
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("dp ef1 gh2"),2);
}

test();
