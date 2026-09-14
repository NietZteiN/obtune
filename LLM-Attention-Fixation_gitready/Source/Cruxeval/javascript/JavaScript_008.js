function f(string, encryption){
    if(encryption === 0){
        return string;
    } else {
        return string.toUpperCase().replace(/[A-Za-z]/g, c => String.fromCharCode(c.charCodeAt(0) + (c.toUpperCase() <= "M" ? 13 : -13)));
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("UppEr", 0),"UppEr");
}

test();
