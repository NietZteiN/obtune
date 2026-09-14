function f(seq, v){
    let a = [];
    seq.forEach(i => {
        if (i.endsWith(v)) {
            a.push(i.repeat(2));
        }
    });
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["oH", "ee", "mb", "deft", "n", "zz", "f", "abA"], "zz"),["zzzz"]);
}

test();
