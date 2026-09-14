function f(text, sep){
    return text.split(sep).slice(0, 3);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a-.-.b", "-."),["a", "", "b"]);
}

test();
