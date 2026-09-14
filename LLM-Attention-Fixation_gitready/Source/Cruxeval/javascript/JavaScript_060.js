function f(doc){
    for(let x of doc){
        if(x.match(/[a-zA-Z]/)){
            return x.toUpperCase();
        }
    }
    return '-';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("raruwa"),"R");
}

test();
