function f(name){
    return [name[0], name[1].split('').reverse().join('')[0]];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("master. "),["m", "a"]);
}

test();
