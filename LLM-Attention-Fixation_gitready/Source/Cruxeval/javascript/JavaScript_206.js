function f(a){
    return a.split(' ').filter(Boolean).join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(" h e l l o   w o r l d! "),"h e l l o w o r l d!");
}

test();
