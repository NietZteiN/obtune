function f(n){
    let values = {0: 3, 1: 4.5, 2: '-'};
    let res = {};
    for (let i in values){
        let j = values[i];
        if (i % n !== 2){
            res[j] = Math.floor(n / 2);
        }
    }
    return Object.keys(res).sort((a, b) => a - b);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(12),[3, 4.5]);
}

test();
