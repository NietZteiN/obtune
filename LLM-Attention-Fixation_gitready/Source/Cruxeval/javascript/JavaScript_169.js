function f(text){
    let ls = text.split('');
    let total = (text.length - 1) * 2;
    for (let i = 1; i <= total; i++) {
        if (i % 2) {
            ls.push('+');
        } else {
            ls.unshift('+');
        }
    }
    return ls.join('').padStart(total);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("taole"),"++++taole++++");
}

test();
