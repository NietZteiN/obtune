function f(text, tabstop){
    text = text.replace(/\n/g, '_____');
    text = text.replace(/\t/g, ' '.repeat(tabstop));
    text = text.replace(/_____/g, '\n');
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`odes	code	well`, 2),"odes  code  well");
}

test();
