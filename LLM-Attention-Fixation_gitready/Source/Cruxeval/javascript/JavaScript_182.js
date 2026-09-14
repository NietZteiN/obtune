function f(dic){
    return Object.entries(dic).sort((a, b) => a[0].localeCompare(b[0]));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"b": 1, "a": 2}),[["a", 2], ["b", 1]]);
}

test();
