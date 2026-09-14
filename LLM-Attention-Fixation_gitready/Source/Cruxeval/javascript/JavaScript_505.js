function f(string){
    while (string) {
        if (string.slice(-1).match(/[a-zA-Z]/)) {
            return string;
        }
        string = string.slice(0, -1);
    }
    return string;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("--4/0-209"),"");
}

test();
