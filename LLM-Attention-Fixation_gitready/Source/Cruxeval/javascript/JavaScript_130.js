function f(m){
    let items = Object.entries(m);
    for(let i = items.length - 2; i >= 0; i--){
        let tmp = items[i]
        items[i] = items[i+1]
        items[i+1] = tmp
    }
    let keys = Object.keys(m);
    return ['{}={}', '{1}={0}'][items.length % 2].replace('{0}', keys[0]).replace('{1}', keys[1]);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"l": 4, "h": 6, "o": 9}),"h=l");
}

test();
