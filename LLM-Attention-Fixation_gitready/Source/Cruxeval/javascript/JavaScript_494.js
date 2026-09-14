function f(num, l){
    let t = "";
    while (l > num.length) {
        t += '0';
        l--;
    }
    return t + num;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("1", 3),"001");
}

test();
