function f(text){
    return /^[\x00-\x7F]*$/.test(text);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("wW의IV]HDJjhgK[dGIUlVO@Ess$coZkBqu[Ct"),false);
}

test();
