function f(text){
    text = text.replace('#', '1').replace('$', '5');
    return text.match(/^\d+$/) ? 'yes' : 'no';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("A"),"no");
}

test();
