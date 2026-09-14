function f(text, value){
    return text.toLowerCase().startsWith(value.toLowerCase()) ? text.slice(value.length) : text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("coscifysu", "cos"),"cifysu");
}

test();
