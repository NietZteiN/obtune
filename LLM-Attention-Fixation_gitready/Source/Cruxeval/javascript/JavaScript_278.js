function f(array1, array2){
    let result = {};
    array1.forEach(key => {
        result[key] = array2.filter(el => key * 2 > el);
    });
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 132], [5, 991, 32, 997]),{0: [], 132: [5, 32]});
}

test();
