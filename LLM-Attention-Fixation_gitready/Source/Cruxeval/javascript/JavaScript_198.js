function f(text, strip_chars){
    return text.split('').reverse().join('').replace(new RegExp(`[${strip_chars}]`), '').split('').reverse().join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("tcmfsmj", "cfj"),"tcmfsm");
}

test();
