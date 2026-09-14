function f(test, sep, maxsplit){
    sep = sep || ' ';
    maxsplit = maxsplit || -1;

    try {
        return test.split(sep, maxsplit);
    } catch (error) {
        return test.split();
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ab cd", "x", 2),["ab cd"]);
}

test();
