function f(text, suffix){
    if(suffix === ''){
        suffix = null;
    }
    return text.endsWith(suffix);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("uMeGndkGh", "kG"),false);
}

test();
