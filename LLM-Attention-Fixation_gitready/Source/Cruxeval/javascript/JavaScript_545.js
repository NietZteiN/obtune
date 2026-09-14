function f(array){
    let result = [];
    let index = 0;
    while (index < array.length) {
        result.push(array.pop());
        index += 2;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([8, 8, -4, -9, 2, 8, -1, 8]),[8, -1, 8]);
}

test();
