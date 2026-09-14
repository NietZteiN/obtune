function f(text){
    if (text.toUpperCase() === text) {
        return 'ALL UPPERCASE';
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hello Is It MyClass"),"Hello Is It MyClass");
}

test();
