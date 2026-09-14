function f(text, oldStr, newStr){
    if (oldStr.length > 3) {
        return text;
    }
    if (text.includes(oldStr) && !text.includes(' ')) {
        return text.replace(new RegExp(oldStr, 'g'), newStr.repeat(oldStr.length));
    }
    while (text.includes(oldStr)) {
        text = text.replace(new RegExp(oldStr, 'g'), newStr);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("avacado", "va", "-"),"a--cado");
}

test();
