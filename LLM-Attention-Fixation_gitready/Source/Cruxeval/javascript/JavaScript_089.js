function f(char){
    if (!['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'].includes(char)) {
        return null;
    }
    if (['A', 'E', 'I', 'O', 'U'].includes(char)) {
        return char.toLowerCase();
    }
    return char.toUpperCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("o"),"O");
}

test();
