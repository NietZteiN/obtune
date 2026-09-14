function f(d, count){
    for (let i = 0; i < count; i++) {
        if (Object.keys(d).length === 0) {
            break;
        }
        delete d[Object.keys(d)[Object.keys(d).length - 1]];
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}, 200),{});
}

test();
