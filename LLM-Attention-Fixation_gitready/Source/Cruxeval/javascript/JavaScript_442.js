function f(lst){
    let res = [];
    for(let i = 0; i < lst.length; i++){
        if (lst[i] % 2 === 0){
            res.push(lst[i]);
        }
    }

    return lst.slice();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, 3, 4]),[1, 2, 3, 4]);
}

test();
