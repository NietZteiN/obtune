function f(text){
    let a = [''];
    let b = '';
    for(let i of text){
        if(i !== ' '){
            a.push(b);
            b = '';
        } else {
            b += i;
        }
    }
    return a.length;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("       "),1);
}

test();
