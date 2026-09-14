function f(text){
    let result = '';
    for(let i = text.length - 1; i >= 0; i--){
        result += text[i];
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("was,"),",saw");
}

test();
