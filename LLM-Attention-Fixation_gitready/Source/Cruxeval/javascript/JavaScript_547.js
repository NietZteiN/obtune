function f(letters){
    let letters_only = letters.replace(/^[\., !?\*]+|[\., !?\*]+$/g, '');
    return letters_only.split(' ').join('....');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("h,e,l,l,o,wo,r,ld,"),"h,e,l,l,o,wo,r,ld");
}

test();
