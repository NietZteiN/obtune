function f(string){
    let tmp = string.toLowerCase();
    for (let char of string.toLowerCase()) {
        if (tmp.includes(char)) {
            tmp = tmp.replace(char, '');
        }
    }
    return tmp;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("[ Hello ]+ Hello, World!!_ Hi"),"");
}

test();
