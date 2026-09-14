function f(text, delim){
    return text.slice(0, text.split('').reverse().join('').indexOf(delim)).split('').reverse().join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("dsj osq wi w", " "),"d");
}

test();
