function f(text){
    let new_text = '';
    text.toLowerCase().trim().split('').forEach(ch => {
        if (!isNaN(ch) || ch.match(/[ÄäÏïÖöÜü]/)) {
            new_text += ch;
        }
    });
    return new_text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(""),"");
}

test();
