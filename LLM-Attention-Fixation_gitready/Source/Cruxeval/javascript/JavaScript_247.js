function f(s){
    if (s.match(/^[a-zA-Z]+$/)) {
        return "yes";
    }
    if (s === "") {
        return "str is empty";
    }
    return "no";
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Boolean"),"yes");
}

test();
