function f(text, char){
    let index = text.lastIndexOf(char);
    let result = text.split('');
    while (index > 0) {
        result[index] = result[index - 1];
        result[index - 1] = char;
        index -= 2;
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qpfi jzm", "j"),"jqjfj zm");
}

test();
