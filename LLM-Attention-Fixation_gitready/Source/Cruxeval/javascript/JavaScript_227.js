function f(text){
    text = text.toLowerCase();
    let head = text[0];
    let tail = text.substring(1);
    return head.toUpperCase() + tail;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Manolo"),"Manolo");
}

test();
