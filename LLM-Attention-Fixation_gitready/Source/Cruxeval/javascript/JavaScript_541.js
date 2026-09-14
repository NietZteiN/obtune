function f(text){
    return text.split('').join('').trim().length === 0;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(` 	  　`),true);
}

test();
