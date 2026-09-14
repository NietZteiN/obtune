function f(text){
    let new_text = text;
    while (text.length > 1 && text[0] === text[text.length - 1]) {
        new_text = text = text.substring(1, text.length - 1);
    }
    return new_text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(")"),")");
}

test();
