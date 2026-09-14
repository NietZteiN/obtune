function f(text, search_chars, replace_chars){
    const trans_table = {};
    for (let i = 0; i < search_chars.length; i++) {
        trans_table[search_chars.charCodeAt(i)] = replace_chars.charCodeAt(i);
    }
    return text.replace(new RegExp('[' + search_chars + ']', 'g'), c => String.fromCharCode(trans_table[c.charCodeAt(0)]));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mmm34mIm", "mm3", ",po"),"pppo4pIp");
}

test();
