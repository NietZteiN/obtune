function f(matrix){
    matrix.reverse();
    let result = [];
    matrix.forEach(primary => {
        Math.max(...primary);
        primary.sort((a, b) => b - a);
        result.push(primary);
    });
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[1, 1, 1, 1]]),[[1, 1, 1, 1]]);
}

test();
