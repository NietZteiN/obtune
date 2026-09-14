function f(string){
    try {
        return string.lastIndexOf('e');
    } catch (error) {
        return "Nuk";
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("eeuseeeoehasa"),8);
}

test();
