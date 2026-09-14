function f(no){
    let d = {};
    no.forEach(item => {
        d[item] = false;
    });
    
    return Object.keys(d).length;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["l", "f", "h", "g", "s", "b"]),6);
}

test();
