function f(text){
    return text.split(' ').map(str => str.trim()).join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("pvtso"),"pvtso");
}

test();
