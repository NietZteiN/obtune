function f(a, b, c){
    let result = {};
    for (let d of [a, b, c]) {
        d.forEach(item => {
            result[item] = undefined;
        });
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 3], [1, 4], [1, 2]),{1: undefined, 2: undefined, 3: undefined, 4: undefined});
}

test();
