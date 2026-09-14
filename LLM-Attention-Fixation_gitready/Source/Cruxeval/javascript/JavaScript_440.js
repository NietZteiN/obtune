function f(text){
    if (!isNaN(text) && !text.includes('.')) {
        return 'yes';
    } else {
        return 'no';
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abc"),"no");
}

test();
