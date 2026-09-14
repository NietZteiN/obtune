function f(text){
    let ls = text.split('');
    let length = ls.length;
    for (let i = 0; i < length; i++) {
        ls.splice(i, 0, ls[i]);
    }
    return ls.join('').padEnd(length * 2, ' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("hzcw"),"hhhhhzcw");
}

test();
