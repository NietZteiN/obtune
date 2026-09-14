function f(text, wrong, right){
    let new_text = text.replace(wrong, right);
    return new_text.toUpperCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("zn kgd jw lnt", "h", "u"),"ZN KGD JW LNT");
}

test();
