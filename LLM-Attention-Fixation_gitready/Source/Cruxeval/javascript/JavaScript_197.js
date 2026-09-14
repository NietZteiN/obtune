function f(temp, timeLimit){
    let s = Math.floor(timeLimit / temp);
    let e = timeLimit % temp;
    return ((s > 1) ? `${s} ${e}` : `${e} oC`);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(1, 1234567890),"1234567890 0");
}

test();
