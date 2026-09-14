function f(x, y){
    let tmp = y.split('').reverse().map(c => c === '9' ? '0' : '9').join('');
    if (parseInt(x).toString() === x && parseInt(tmp).toString() === tmp){
        return x + tmp;
    } else {
        return x;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("", "sdasdnakjsda80"),"");
}

test();
