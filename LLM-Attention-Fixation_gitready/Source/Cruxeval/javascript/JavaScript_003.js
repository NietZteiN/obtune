function f(text, value){
    var text_list = text.split('');
    text_list.push(value);
    return text_list.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("bcksrut", "q"),"bcksrutq");
}

test();
