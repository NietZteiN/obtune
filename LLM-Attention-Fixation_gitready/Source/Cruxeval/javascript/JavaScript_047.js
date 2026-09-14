function f(text){
    var length = text.length;
    var half = Math.floor(length / 2);
    var encode = text.slice(0, half);
    var decode = new TextEncoder().encode(encode);
    if (text.slice(half) === new TextDecoder().decode(decode)) {
        return true;
    } else {
        return false;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("bbbbr"),false);
}

test();
