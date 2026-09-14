function f(text){
    if (text.match(/^\w+$/)) {
        return text.split('').filter(c => /\d/.test(c)).join('');
    } else {
        return text.split('').join('');
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("816"),"816");
}

test();
