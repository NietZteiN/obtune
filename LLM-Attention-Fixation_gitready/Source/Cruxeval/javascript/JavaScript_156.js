function f(text, limit, char){
    if (limit < text.length) {
        return text.substring(0, limit);
    }
    return text.padEnd(limit, char);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("tqzym", 5, "c"),"tqzym");
}

test();
