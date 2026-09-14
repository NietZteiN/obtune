function f(text, value){
    var length = text.length;
    var letters = text.split("");
    if (!letters.includes(value)) {
        value = letters[0];
    }
    return value.repeat(length);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ldebgp o", "o"),"oooooooo");
}

test();
