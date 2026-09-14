function f(total, arg){
    if (Array.isArray(arg)) {
        for (let e of arg) {
            total.push(...e);
        }
    } else {
        total.push(...arg);
    }
    return total;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["1", "2", "3"], "nammo"),["1", "2", "3", "n", "a", "m", "m", "o"]);
}

test();
