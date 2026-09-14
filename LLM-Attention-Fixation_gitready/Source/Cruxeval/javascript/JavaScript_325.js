function f(s){
    let l = s.split('');
    for(let i = 0; i < l.length; i++){
        l[i] = l[i].toLowerCase();
        if (isNaN(l[i])) {
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(""),true);
}

test();
