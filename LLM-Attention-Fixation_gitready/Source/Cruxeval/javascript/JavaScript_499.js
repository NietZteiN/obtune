function f(text, length, fillchar){
    let size = text.length;
    let start = Math.ceil((length - size) / 2);
    return fillchar.repeat(start) + text + fillchar.repeat(length - size - start);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("magazine", 25, "."),".........magazine........");
}

test();
