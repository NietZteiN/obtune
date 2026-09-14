function f(text, digit){
    var count = text.split(digit).length - 1;
    return parseInt(digit) * count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("7Ljnw4Lj", "7"),7);
}

test();
