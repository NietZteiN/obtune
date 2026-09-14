function f(text, prefix){
    let prefix_length = prefix.length;
    if (text.startsWith(prefix)) {
        return text.substr((prefix_length - 1) / 2, (prefix_length + 1) / 2 * -1).split('').reverse().join('');
    } else {
        return text;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("happy", "ha"),"");
}

test();
