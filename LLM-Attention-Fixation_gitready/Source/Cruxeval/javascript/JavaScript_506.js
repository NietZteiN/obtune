function f(n){
    let p = '';
    if(n % 2 === 1){
        p += 'sn';
    } else {
        return n * n;
    }
    for(let x = 1; x <= n; x++){
        if(x % 2 === 0){
            p += 'to';
        } else {
            p += 'ts';
        }
    }
    return p;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(1),"snts");
}

test();
