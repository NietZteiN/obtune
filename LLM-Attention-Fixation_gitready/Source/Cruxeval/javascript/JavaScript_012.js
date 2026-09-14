function f(s, x){
    let count = 0;
    while (s.substring(0, x.length) === x && count < s.length - x.length) {
        s = s.substring(x.length);
        count += x.length;
    }
    return s;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("If you want to live a happy life! Daniel", "Daniel"),"If you want to live a happy life! Daniel");
}

test();
