function f(text, character){
    var subject = text.substring(text.lastIndexOf(character));
    return subject.repeat(text.split(character).length - 1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("h ,lpvvkohh,u", "i"),"");
}

test();
