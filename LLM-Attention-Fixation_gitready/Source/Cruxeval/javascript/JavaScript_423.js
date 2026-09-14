function f(selfie){
    let lo = selfie.length;
    for(let i = lo - 1; i > -1; i--){
        if(selfie[i] === selfie[0]){
            selfie.pop();
        }
    }
    return selfie;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([4, 2, 5, 1, 3, 2, 6]),[4, 2, 5, 1, 3, 2]);
}

test();
