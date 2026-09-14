function f(n, l){
    let archive = {};
    for (let i = 0; i < n; i++) {
        archive = {};
        l.forEach(x => {
            archive[x + 10] = x * 10;
        });
    }
    return archive;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(0, ["aaa", "bbb"]),{});
}

test();
