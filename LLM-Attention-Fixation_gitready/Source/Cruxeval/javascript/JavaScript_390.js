function f(text){
    if (!text.trim()){
        return text.trim().length;
    }
    return null;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(` 	 `),0);
}

test();
