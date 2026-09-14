function f(a, b){
    return {...a, ...b};
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"w": 5, "wi": 10}, {"w": 3}),{"w": 3, "wi": 10});
}

test();
