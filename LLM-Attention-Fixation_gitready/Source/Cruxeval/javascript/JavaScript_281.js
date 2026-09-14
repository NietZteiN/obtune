function f(c, index, value){
    c[index] = value;
    if (value >= 3) {
        c['message'] = 'xcrWt';
    } else {
        delete c['message'];
    }
    return c;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({1: 2, 3: 4, 5: 6, "message": "qrTHo"}, 8, 2),{1: 2, 3: 4, 5: 6, 8: 2});
}

test();
