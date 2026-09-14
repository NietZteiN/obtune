function f(s){
    if (s.slice(-5).match(/^[\x00-\x7F]+$/)) {
        return [s.slice(-5), s.slice(0, 3)];
    } else if (s.slice(0, 5).match(/^[\x00-\x7F]+$/)) {
        return [s.slice(0, 5), s.slice(-2)];
    } else {
        return s;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a1234år"),["a1234", "år"]);
}

test();
