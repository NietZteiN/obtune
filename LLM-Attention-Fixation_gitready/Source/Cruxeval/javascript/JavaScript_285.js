function f(text, ch){
    return text.split(ch).length - 1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("This be Pirate's Speak for 'help'!", " "),5);
}

test();
