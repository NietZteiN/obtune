function f(text, position, value){
    let length = text.length;
    let index = position % length;
    if (position < 0) {
        index = Math.floor(length / 2);
    }
    let new_text = text.split('');
    new_text.splice(index, 0, value);
    new_text.splice(length - 1, 1);
    return new_text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("sduyai", 1, "y"),"syduyi");
}

test();
