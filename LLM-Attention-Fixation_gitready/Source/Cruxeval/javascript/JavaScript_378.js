function f(dic, key){
    if(!dic.hasOwnProperty(key)) {
        return 'No such key!'
    }
    else {
        let value = dic[key];
        delete dic[key];
        return value;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"did": 0}, "u"),"No such key!");
}

test();
