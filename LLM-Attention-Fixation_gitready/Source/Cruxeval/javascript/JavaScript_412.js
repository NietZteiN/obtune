function f(start, end, interval){
    let steps = [];
    for(let i = start; i <= end; i += interval){
        steps.push(i);
    }
    if (steps.includes(1)){
        steps[steps.length - 1] = end + 1;
    }
    return steps.length;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(3, 10, 1),8);
}

test();
