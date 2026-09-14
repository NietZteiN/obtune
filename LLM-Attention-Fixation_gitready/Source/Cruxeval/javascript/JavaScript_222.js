function f(mess, char){
    while (mess.lastIndexOf(char) !== -1 && mess.indexOf(char, mess.lastIndexOf(char) + 1) !== -1) {
        mess = mess.slice(0, mess.lastIndexOf(char) + 1) + mess.slice(mess.lastIndexOf(char) + 2);
    }
    return mess;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("0aabbaa0b", "a"),"0aabbaa0b");
}

test();
