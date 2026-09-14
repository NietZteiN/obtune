function f(s){
    let b = '';
    let c = '';
    for (let i of s){
        c = c + i;
        if (s.lastIndexOf(c) > -1){
            return s.lastIndexOf(c);
        }
    }
    return 0;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("papeluchis"),2);
}

test();
