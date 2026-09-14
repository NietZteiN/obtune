function f(a){
    a = a.replace('/', ':');
    let z = a.split(':');
    return [z[0], ':', z[1]];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("/CL44     "),["", ":", "CL44     "]);
}

test();
