function f(text, chars){
    let num_applies = 2;
    let extra_chars = '';
    for (let i = 0; i < num_applies; i++) {
        extra_chars += chars;
        text = text.replace(new RegExp(extra_chars, 'g'), '');
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("zbzquiuqnmfkx", "mk"),"zbzquiuqnmfkx");
}

test();
