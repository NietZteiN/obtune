function f(text){
    return Math.max(...Array.from('aeiou', ch => text.indexOf(ch)));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qsqgijwmmhbchoj"),13);
}

test();
