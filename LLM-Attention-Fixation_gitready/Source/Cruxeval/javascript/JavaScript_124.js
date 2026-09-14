function f(txt, sep, sep_count){
    let o = '';
    while (sep_count > 0 && txt.split(sep).length > 1) {
        o += txt.substring(0, txt.lastIndexOf(sep) + sep.length);
        txt = txt.substring(txt.lastIndexOf(sep) + sep.length);
        sep_count--;
    }
    return o + txt;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("i like you", " ", -1),"i like you");
}

test();
