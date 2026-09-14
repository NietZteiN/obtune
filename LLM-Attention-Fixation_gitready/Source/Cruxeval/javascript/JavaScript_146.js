function f(single_digit){
    let result = [];
    for(let c = 1; c < 11; c++){
        if(c !== single_digit){
            result.push(c);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(5),[1, 2, 3, 4, 6, 7, 8, 9, 10]);
}

test();
