function f(concat, di){
    let count = Object.keys(di).length;
    for (let i = 0; i < count; i++) {
        if (di[i.toString()] && concat.includes(di[i.toString()])) {
            delete di[i.toString()];
        }
    }
    return "Done!";
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mid", {"0": "q", "1": "f", "2": "w", "3": "i"}),"Done!");
}

test();
