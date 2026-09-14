function f(name){
    return name.split(' ').join('*');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Fred Smith"),"Fred*Smith");
}

test();
