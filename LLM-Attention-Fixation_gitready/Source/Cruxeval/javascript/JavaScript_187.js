function f(d, index){
    var length = Object.keys(d).length;
    var idx = index % length;
    var keys = Object.keys(d);
    var v = d[keys[keys.length - 1]];
    for (var i = 0; i < idx; i++) {
        delete d[keys.pop()];
    }
    return v;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({27: 39}, 1),39);
}

test();
