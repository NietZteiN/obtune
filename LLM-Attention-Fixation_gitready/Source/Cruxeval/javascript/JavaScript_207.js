function f(commands){
    let d = {};
    for (let c of commands) {
        Object.assign(d, c);
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([{"brown": 2}, {"blue": 5}, {"bright": 4}]),{"brown": 2, "blue": 5, "bright": 4});
}

test();
