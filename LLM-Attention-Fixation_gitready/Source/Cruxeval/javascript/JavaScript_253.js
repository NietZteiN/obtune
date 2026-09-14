function f(text, pref){
    var length = pref.length;
    if (pref === text.slice(0, length)) {
        return text.slice(length);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("kumwwfv", "k"),"umwwfv");
}

test();
