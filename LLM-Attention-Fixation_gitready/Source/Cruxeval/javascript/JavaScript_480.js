function f(s, c1, c2){
    if (s === ''){
        return s;
    }
    let ls = s.split(c1);
    for (let index = 0; index < ls.length; index++){
        let item = ls[index];
        if (item.includes(c1)){
            ls[index] = item.replace(c1, c2);
        }
    }
    return ls.join(c1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("", "mi", "siast"),"");
}

test();
