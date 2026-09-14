function f(numbers, num, val){
    while (numbers.length < num) {
        numbers.splice(Math.floor(numbers.length / 2), 0, val);
    }
    for (let i = 0; i < Math.floor(numbers.length / (num - 1)) - 4; i++) {
        numbers.splice(Math.floor(numbers.length / 2), 0, val);
    }
    return numbers.join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([], 0, 1),"");
}

test();
