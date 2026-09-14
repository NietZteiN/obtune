function f(strings, substr){
    let list = strings.filter(s => s.startsWith(substr));
    return list.sort((a, b) => a.length - b.length);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["condor", "eyes", "gay", "isa"], "d"),[]);
}

test();
