function f(text, tab_size){
    let res = '';
    text = text.replace(/\t/g, ' '.repeat(tab_size-1));
    for(let i = 0; i < text.length; i++) {
        if(text[i] === ' ') {
            res += '|';
        } else {
            res += text[i];
        }
    }
    return res;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`	a`, 3),"||a");
}

test();
