function f(name){
    if (name === name.toLowerCase()) {
        return name.toUpperCase();
    } else {
        return name.toLowerCase();
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Pinneaple"),"pinneaple");
}

test();
