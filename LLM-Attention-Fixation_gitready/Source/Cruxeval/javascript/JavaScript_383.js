function f(text, chars){
    let result = text.split('');
    while (result.slice(-3, 0, -2).includes(chars)) {
        result.splice(-3, 2);
    }
    return result.join('').trim('.');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ellod!p.nkyp.exa.bi.y.hain", ".n.in.ha.y"),"ellod!p.nkyp.exa.bi.y.hain");
}

test();
