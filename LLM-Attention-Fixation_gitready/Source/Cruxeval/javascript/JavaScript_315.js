function f(challenge){
    return challenge.toLowerCase().replace('l', ',');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("czywZ"),"czywz");
}

test();
