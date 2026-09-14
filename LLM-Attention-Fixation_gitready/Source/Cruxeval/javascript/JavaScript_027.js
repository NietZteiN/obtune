function f(w){
    let ls = w.split('');
    let omw = '';
    while (ls.length > 0) {
        omw += ls.shift();
        if (ls.length * 2 > w.length) {
            return w.substring(ls.length) === omw;
        }
    }
    return false;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("flak"),false);
}

test();
