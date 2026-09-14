function f(text, pref){
    if(Array.isArray(pref)){
        return pref.map(x => text.startsWith(x)).join(', ');
    } else {
        return text.startsWith(pref);
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hello World", "W"),false);
}

test();
