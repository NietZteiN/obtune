function f(text, value){
    let parts = text.split(value);
    return parts[1] + parts[0];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("difkj rinpx", "k"),"j rinpxdif");
}

test();
