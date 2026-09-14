function f(text, value){
    if (!text.includes(value)) {
        return '';
    }
    return text.substring(0, text.lastIndexOf(value));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mmfbifen", "i"),"mmfb");
}

test();
