function f(s){
    let r = [];
    for (let i = s.length - 1; i >= 0; i--) {
        r.push(s[i]);
    }
    return r.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("crew"),"werc");
}

test();
