function f(text, char){
    if (!text.endsWith(char)){
        return f(char + text, char);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("staovk", "k"),"staovk");
}

test();
