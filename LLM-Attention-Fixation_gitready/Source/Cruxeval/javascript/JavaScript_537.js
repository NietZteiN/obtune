function f(text, value){
    let new_text = text.split('');
    try {
        new_text.push(value);
        var length = new_text.length;
    } catch(error) {
        length = 0;
    }
    return '[' + length + ']';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abv", "a"),"[4]");
}

test();
