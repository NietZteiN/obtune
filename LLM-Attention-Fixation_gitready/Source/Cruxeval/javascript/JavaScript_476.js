function f(a, split_on){
    let t = a.split(' ');
    let b = [];
    for (let i of t) {
        for (let j of i) {
            b.push(j);
        }
    }
    if (b.includes(split_on)) {
        return true;
    } else {
        return false;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("booty boot-boot bootclass", "k"),false);
}

test();
