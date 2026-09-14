function f(postcode){
    return postcode.substring(postcode.indexOf('C'));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ED20 CW"),"CW");
}

test();
