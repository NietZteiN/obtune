function f(lst){
    let result = [];
    let i = lst.length - 1;
    for(let _ of lst) {
        if (i % 2 === 0) {
            result.push(-lst[i]);
        } else {
            result.push(lst[i]);
        }
        i -= 1;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 7, -1, -3]),[-3, 1, 7, -1]);
}

test();
