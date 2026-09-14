function f(numbers){
    let floats = numbers.map(n => n % 1);
    return floats.includes(1) ? floats : [];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119]),[]);
}

test();
