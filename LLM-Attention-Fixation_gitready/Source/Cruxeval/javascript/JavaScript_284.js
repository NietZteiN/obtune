function f(text, prefix){
    let idx = 0;
    for (let letter of prefix) {
        if (text[idx] !== letter) {
            return null;
        }
        idx++;
    }
    return text.slice(idx);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("bestest", "bestest"),"");
}

test();
