function f(cart){
    while (Object.keys(cart).length > 5) {
        delete cart[Object.keys(cart)[Object.keys(cart).length - 1]];
    }
    return cart;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),{});
}

test();
