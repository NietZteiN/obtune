function f(price, product){
    let inventory = ['olives', 'key', 'orange'];
    if (!inventory.includes(product)) {
        return price;
    } else {
        price *= 0.85;
        inventory.splice(inventory.indexOf(product), 1);
    }
    return price;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(8.5, "grapes"),8.5);
}

test();
