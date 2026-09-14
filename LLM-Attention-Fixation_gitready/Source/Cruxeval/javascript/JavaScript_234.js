function f(text, char){
    let position = text.length;
    if (text.includes(char)) {
        position = text.indexOf(char);
        if (position > 1) {
            position = (position + 1) % text.length;
        }
    }
    return position;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("wduhzxlfk", "w"),0);
}

test();
