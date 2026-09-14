function f(text){
    let g, field;
    field = text.replace(/ /g, '');
    g = text.replace(/0/g, ' ');
    text = text.replace(/1/g, 'i');

    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("00000000 00000000 01101100 01100101 01101110"),"00000000 00000000 0ii0ii00 0ii00i0i 0ii0iii0");
}

test();
