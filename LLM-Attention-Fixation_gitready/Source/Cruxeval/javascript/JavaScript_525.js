function f(c, st, ed){
    let d = {};
    let a = 0;
    let b = 0;
    for (let x in c) {
        let y = c[x];
        d[y] = x;
        if (y === st) {
            a = x;
        }
        if (y === ed) {
            b = x;
        }
    }
    let w = d[st];
    return (a > b) ? [w, b] : [b, w];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"TEXT": 7, "CODE": 3}, 7, 3),["TEXT", "CODE"]);
}

test();
