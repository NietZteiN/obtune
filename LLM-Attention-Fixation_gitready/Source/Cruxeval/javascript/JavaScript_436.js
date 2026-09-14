function f(s, characters){
    return characters.map(index => s.substring(index, index + 1));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("s7 6s 1ss", [1, 3, 6, 1, 2]),["7", "6", "1", "7", " "]);
}

test();
