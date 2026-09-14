function f(zoo){
    return Object.fromEntries(Object.entries(zoo).map(([key, value]) => [value, key]));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"AAA": "fr"}),{"fr": "AAA"});
}

test();
