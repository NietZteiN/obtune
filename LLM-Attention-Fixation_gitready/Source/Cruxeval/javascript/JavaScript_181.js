function f(s){
    let count = 0;
    let digits = "";
    for(let i = 0; i < s.length; i++){
        let c = s[i];
        if(!isNaN(c)){
            count++;
            digits += c;
        }
    }
    return [digits, count];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qwfasgahh329kn12a23"),["3291223", 7]);
}

test();
