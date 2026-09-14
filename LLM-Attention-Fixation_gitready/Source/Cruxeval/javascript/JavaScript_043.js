function f(n){
    for(let i of n.toString()){
        if (!Number.isInteger(parseInt(i))) {
            n = -1;
            break;
        }
    }
    return n;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("6 ** 2"),-1);
}

test();
