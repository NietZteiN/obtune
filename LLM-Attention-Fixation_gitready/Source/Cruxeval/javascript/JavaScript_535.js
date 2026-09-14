function f(n){
    n = n.toString();
    for (let i = 0; i < n.length; i++) {
        if (!["0", "1", "2"].includes(n[i]) && !Array.from({length: 5}, (_, index) => index + 5).includes(parseInt(n[i]))) {
            return false;
        }
    }
    return true;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(1341240312),false);
}

test();
