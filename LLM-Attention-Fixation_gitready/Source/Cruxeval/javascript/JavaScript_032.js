function f(s, sep){
    let reverse = s.split(sep).map(e => '*' + e);
    return reverse.reverse().join(';');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("volume", "l"),"*ume;*vo");
}

test();
