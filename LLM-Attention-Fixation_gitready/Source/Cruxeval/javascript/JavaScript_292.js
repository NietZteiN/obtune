function f(text){
    var newText = text.split('').map(c => c.match(/\d/) ? c : '*');
    return newText.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("5f83u23saa"),"5*83*23***");
}

test();
