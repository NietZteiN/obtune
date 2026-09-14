function f(text, suffix){
    text += suffix;
    while (text.slice(-suffix.length) === suffix) {
        text = text.slice(0, -1);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("faqo osax f", "f"),"faqo osax ");
}

test();
