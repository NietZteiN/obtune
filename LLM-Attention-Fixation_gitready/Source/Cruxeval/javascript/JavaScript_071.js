function f(d, n){
    for(let i = 0; i < n; i++){
        let item = Object.entries(d).pop();
        delete d[item[0]];
        d[item[1]] = parseInt(item[0]);
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({1: 2, 3: 4, 5: 6, 7: 8, 9: 10}, 1),{1: 2, 3: 4, 5: 6, 7: 8, 10: 9});
}

test();
