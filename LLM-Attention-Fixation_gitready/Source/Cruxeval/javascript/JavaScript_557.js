function f(s) {
    let d = s.lastIndexOf('ar');
    if (d === -1) {
        return s;
    }
    return s.substring(0, d) + ' ar ' + s.substring(d + 2);
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("xxxarmmarxx"),"xxxarmm ar xx");
}

test();
