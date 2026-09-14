function f(array, elem){
    elem = elem.toString();
    let d = 0;
    for(let i of array){
        if(i.toString() === elem){
            d++;
        }
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-1, 2, 1, -8, -8, 2], 2),2);
}

test();
