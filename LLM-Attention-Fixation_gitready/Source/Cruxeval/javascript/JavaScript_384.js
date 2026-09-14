function f(text, chars){
    chars = chars.split('');
    text = text.split('');
    let new_text = text;
    while (new_text.length > 0 && text.length > 0) {
        if (chars.includes(new_text[0])) {
            new_text = new_text.slice(1);
        } else {
            break;
        }
    }
    return new_text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("asfdellos", "Ta"),"sfdellos");
}

test();
