function f(text, to_place){
    var after_place = text.slice(0, text.indexOf(to_place) + 1);
    var before_place = text.slice(text.indexOf(to_place) + 1);
    return after_place + before_place;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("some text", "some"),"some text");
}

test();
