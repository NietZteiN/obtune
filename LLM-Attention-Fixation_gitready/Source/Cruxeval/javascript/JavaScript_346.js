function f(filename){
    var suffix = filename.split('.').pop();
    var f2 = filename + suffix.split('').reverse().join('');
    return f2.endsWith(suffix);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("docs.doc"),false);
}

test();
