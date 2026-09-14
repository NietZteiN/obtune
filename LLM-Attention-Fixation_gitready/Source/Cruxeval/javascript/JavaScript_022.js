function f(a){
    if (a === 0) {
        return [0];
    }
    let result = [];
    while (a > 0) {
        result.push(a % 10);
        a = Math.floor(a / 10);
    }
    result.reverse();
    return parseInt(result.join(''));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(0),[0]);
}

test();
