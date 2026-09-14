function f(text){
    let uppers = 0;
    for(let c of text){
        if(c === c.toUpperCase()){
            uppers++;
        }
    }
    return uppers >= 10 ? text.toUpperCase() : text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("?XyZ"),"?XyZ");
}

test();
