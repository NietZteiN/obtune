function f(numbers, index){
    for(let n of numbers.slice(index)){
        numbers.splice(index, 0, n);
        index += 1;
    }
    return numbers.slice(0, index);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([-2, 4, -4], 0),[-2, 4, -4]);
}

test();
