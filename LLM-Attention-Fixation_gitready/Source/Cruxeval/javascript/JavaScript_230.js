function f(text){
    let result = '';
    let i = text.length - 1;
    while (i >= 0) {
        let c = text[i];
        if (c.match(/[a-zA-Z]/)) {
            result += c;
        }
        i--;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("102x0zoq"),"qozx");
}

test();
