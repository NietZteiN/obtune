function f(val, text){
    let indices = [];
    for (let index = 0; index < text.length; index++) {
        if (text[index] === val) {
            indices.push(index);
        }
    }
    if (indices.length === 0) {
        return -1;
    } else {
        return indices[0];
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("o", "fnmart"),-1);
}

test();
