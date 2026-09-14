function f(a, b){
    for (let key in b) {
        if (!a.hasOwnProperty(key)) {
            a[key] = [b[key]];
        } else {
            a[key].push(b[key]);
        }
    }
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}, {"foo": "bar"}),{"foo": ["bar"]});
}

test();
