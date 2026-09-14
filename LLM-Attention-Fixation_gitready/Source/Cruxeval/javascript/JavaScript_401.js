function f(text, suffix){
    if(suffix && text.endsWith(suffix)){
        return text.slice(0, -suffix.length);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mathematics", "example"),"mathematics");
}

test();
