function f(text, delim){
    let [first, second] = text.split(delim);
    return second + delim + first;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("bpxa24fc5.", "."),".bpxa24fc5");
}

test();
