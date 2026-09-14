function f(text, suffix, num){
    var str_num = num.toString();
    return text.endsWith(suffix + str_num);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("friends and love", "and", 3),false);
}

test();
