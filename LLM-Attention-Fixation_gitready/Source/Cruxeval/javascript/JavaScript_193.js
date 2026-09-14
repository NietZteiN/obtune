function f(string){
    let count = (string.match(/:/g) || []).length;
    return string.replace(':', '', count - 1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("1::1"),"1:1");
}

test();
