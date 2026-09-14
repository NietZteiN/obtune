function f(update, starting){
    let d = Object.assign({}, starting);
    for (let k in update) {
        if (k in d) {
            d[k] += update[k];
        } else {
            d[k] = update[k];
        }
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}, {"desciduous": 2}),{"desciduous": 2});
}

test();
