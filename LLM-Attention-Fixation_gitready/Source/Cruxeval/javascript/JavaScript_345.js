function f(a, b){
    if (a < b) {
        return [b, a];
    }
    return [a, b];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ml", "mv"),["mv", "ml"]);
}

test();
