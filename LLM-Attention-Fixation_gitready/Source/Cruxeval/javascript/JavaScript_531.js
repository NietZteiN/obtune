function f(text, x) {
    if (!text.startsWith(x)) {
        return f(text.substring(1), x);
    } else {
        return text;
    }
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Ibaskdjgblw asdl ", "djgblw"),"djgblw asdl ");
}

test();
