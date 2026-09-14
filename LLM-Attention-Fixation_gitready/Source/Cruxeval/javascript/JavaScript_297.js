function f(num){
    if (num > 0 && num < 1000 && num !== 6174) {
        return 'Half Life';
    }
    return 'Not found';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(6173),"Not found");
}

test();
