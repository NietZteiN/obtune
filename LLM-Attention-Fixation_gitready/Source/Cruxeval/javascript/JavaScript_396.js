function f(ets){
    while (Object.keys(ets).length > 0) {
        let key = Object.keys(ets)[0];
        let value = ets[key];
        delete ets[key];
        ets[key] = value ** 2;
    }
    return ets;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),{});
}

test();
