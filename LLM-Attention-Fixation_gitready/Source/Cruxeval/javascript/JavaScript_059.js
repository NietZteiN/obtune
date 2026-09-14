function f(s){
    let a = s.split('').filter(char => char !== ' ');
    let b = a.slice();
    for(let i = a.length - 1; i >= 0; i--){
        if(a[i] === ' '){
            b.pop();
        } else {
            break;
        }
    }
    return b.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("hi "),"hi");
}

test();
