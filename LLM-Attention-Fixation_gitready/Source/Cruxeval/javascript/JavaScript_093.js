function f(n){
    let length = n.length + 2;
    let revn = n.split('');
    let result = revn.join('');
    revn = [];
    return result + '!'.repeat(length);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("iq"),"iq!!!!");
}

test();
