function f(text, char){
    text = text.split('');
    for (let i = 0; i < text.length; i++) {
        if (text[i] === char) {
            text.splice(i, 1);
            return text.join('');
        }
    }
    return text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("pn", "p"),"n");
}

test();
