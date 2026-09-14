function f(user){
    if (Object.keys(user).length > Object.values(user).length) {
        return Object.keys(user);
    }
    return Object.values(user);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"eating": "ja", "books": "nee", "piano": "coke", "excitement": "zoo"}),["ja", "nee", "coke", "zoo"]);
}

test();
