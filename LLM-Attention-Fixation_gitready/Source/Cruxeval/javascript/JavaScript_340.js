function f(text){
    let uppercase_index = text.indexOf('A');
    if (uppercase_index >= 0) {
        return text.substring(0, uppercase_index) + text.substring(text.indexOf('a') + 1);
    } else {
        return text.split('').sort().join('');
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("E jIkx HtDpV G"),"   DEGHIVjkptx");
}

test();
