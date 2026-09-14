function f(needle, haystack){
    let count = 0;
    while (haystack.includes(needle)) {
        haystack = haystack.replace(needle, '');
        count++;
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a", "xxxaaxaaxx"),4);
}

test();
