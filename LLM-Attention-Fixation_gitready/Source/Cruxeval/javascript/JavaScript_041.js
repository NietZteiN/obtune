function f(array, values){
    array.reverse();
    values.forEach(value => {
        array.splice(Math.floor(array.length / 2), 0, value);
    });
    array.reverse();
    return array;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([58], [21, 92]),[58, 92, 21]);
}

test();
