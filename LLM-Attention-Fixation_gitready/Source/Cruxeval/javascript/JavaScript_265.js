function f(d, k){
    let new_d = {};
    for(let key in d){
        if(key < k){
            new_d[key] = d[key];
        }
    }
    return new_d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({1: 2, 2: 4, 3: 3}, 3),{1: 2, 2: 4});
}

test();
