function f(input){
    let amount = input instanceof Array ? input.length : 0;
    if (typeof input === 'object') {
        amount = Object.keys(input).length;
    }
    let nonzero = amount > 0 ? amount : 0;
    return nonzero;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(1),0);
}

test();
