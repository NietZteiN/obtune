function f(text){
    text = text.split('');
    for (let i = text.length - 1; i >= 0; i--) {
        if (text[i] === ' ') {
            text[i] = '&nbsp;';
        }
    }
    return text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("   "),"&nbsp;&nbsp;&nbsp;");
}

test();
