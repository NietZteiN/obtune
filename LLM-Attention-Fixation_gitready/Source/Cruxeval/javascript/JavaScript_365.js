function f(n, s){
    if(s.startsWith(n)){
        let [pre, _] = s.split(n, 2);
        return pre + n + s.substring(n.length);
    }
    return s;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("xqc", "mRcwVqXsRDRb"),"mRcwVqXsRDRb");
}

test();
