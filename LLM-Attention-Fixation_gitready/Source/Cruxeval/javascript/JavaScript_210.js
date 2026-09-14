function f(n, m, num){
    let x_list = Array.from({length: m - n + 1}, (_, index) => n + index);
    let j = 0;
    while (true) {
        j = (j + num) % x_list.length;
        if (x_list[j] % 2 === 0) {
            return x_list[j];
        }
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(46, 48, 21),46);
}

test();
