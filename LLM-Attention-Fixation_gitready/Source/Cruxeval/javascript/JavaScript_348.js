function f(dictionary){
    return Object.assign({}, dictionary);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({563: 555, 133: undefined}),{563: 555, 133: undefined});
}

test();
