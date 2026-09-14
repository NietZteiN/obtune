function f(text, char){
    return text.split(char).join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a", "a")," ");
}

test();
