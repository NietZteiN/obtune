function f(text, c){
    let ls = text.split('');
    if (!text.includes(c)) {
        throw new Error(`Text has no ${c}`);
    }
    ls.splice(text.lastIndexOf(c), 1);
    return ls.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("uufhl", "l"),"uufh");
}

test();
