function f(n){
    let t = 0;
    let b = '';
    let digits = Array.from(String(n), Number);
    for(let d of digits){
        if(d === 0){
            t += 1;
        } else {
            break;
        }
    }
    for(let i = 0; i < t; i++){
        b += '1' + '0' + '4';
    }
    b += String(n);
    return b;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(372359),"372359");
}

test();
