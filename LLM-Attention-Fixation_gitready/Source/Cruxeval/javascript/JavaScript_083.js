function f(text){
    let l = text.split('0').slice(-2);
    if (l[1] === '') {
        return '-1:-1';
    }
    return `${l[0].length}:${l[1].indexOf("0") + 1}`;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qq0tt"),"2:0");
}

test();
