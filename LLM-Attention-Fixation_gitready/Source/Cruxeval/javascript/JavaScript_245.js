function f(alphabet, s){
    let a = [...alphabet].filter(x => s.includes(x.toUpperCase()));
    if (s.toUpperCase() === s) {
        a.push('all_uppercased');
    }
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abcdefghijklmnopqrstuvwxyz", "uppercased # % ^ @ ! vz."),[]);
}

test();
