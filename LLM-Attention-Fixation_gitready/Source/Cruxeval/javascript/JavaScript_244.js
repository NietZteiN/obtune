function f(text, symbols){
    let count = 0;
    if (symbols) {
        for (let i = 0; i < symbols.length; i++) {
            count += 1;
        }
        text = text.repeat(count);
    }
    return text.padStart(text.length + count*2).slice(0, -2);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("", "BC1ty"),"        ");
}

test();
