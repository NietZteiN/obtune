function f(l, c){
    return l.join(c);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["many", "letters", "asvsz", "hello", "man"], ""),"manylettersasvszhelloman");
}

test();
