function f(text, n){
    if (text.length <= 2){
        return text;
    }
    let leading_chars = text[0].repeat(n - text.length + 1);
    return leading_chars + text.slice(1, -1) + text.slice(-1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("g", 15),"g");
}

test();
