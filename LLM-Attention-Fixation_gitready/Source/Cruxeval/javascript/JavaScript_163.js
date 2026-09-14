function f(text, space_symbol, size){
    let spaces = space_symbol.repeat(Math.max(size - text.length, 0));
    return text + spaces;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("w", "))", 7),"w))))))))))))");
}

test();
