function f(text, amount){
    let length = text.length;
    let pre_text = '|';

    if (amount >= length) {
        let extra_space = amount - length;
        pre_text += ' '.repeat(Math.floor(extra_space / 2));
        return pre_text + text + pre_text;
    }
    
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("GENERAL NAGOOR", 5),"GENERAL NAGOOR");
}

test();
