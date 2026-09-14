function f(text){
    let ls = text.split('');
    for (let i = 0; i < ls.length; i++) {
        if (ls[i] !== '+') {
            ls.splice(i, 0, '*', '+');
            break;
        }
    }
    return ls.join('+');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("nzoh"),"*+++n+z+o+h");
}

test();
