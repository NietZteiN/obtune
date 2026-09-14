function f(x){
    if(x === x.toLowerCase()){
        return x;
    } else {
        return x.split('').reverse().join('');
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ykdfhp"),"ykdfhp");
}

test();
