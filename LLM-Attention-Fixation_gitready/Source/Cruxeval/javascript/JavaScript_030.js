function f(array){
    let result = [];
    for (let elem of array) {
        if (elem.length === 1 || (Number.isInteger(elem) && !Math.abs(elem).toString().length === 1)) {
            result.push(elem);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["a", "b", "c"]),["a", "b", "c"]);
}

test();
