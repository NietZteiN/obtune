function f(d){
    const sortedPairs = Object.entries(d).sort((a, b) => (a[0].toString() + a[1].toString()).length - (b[0].toString() + b[1].toString()).length);
    return sortedPairs.filter(pair => pair[0] < pair[1]);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({55: 4, 4: 555, 1: 3, 99: 21, 499: 4, 71: 7, 12: 6}),[[1, 3], [4, 555]]);
}

test();
