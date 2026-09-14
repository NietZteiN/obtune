function f(text, fill, size){
    if (size < 0) {
        size = Math.abs(size);
    }
    if (text.length > size) {
        return text.slice(text.length - size);
    }
    return text.padStart(size, fill);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("no asw", "j", 1),"w");
}

test();
