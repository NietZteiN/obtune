function f(arr){
    let n = arr.filter(item => item % 2 === 0);
    let m = n.concat(arr);
    for(let i of m){
        if(m.indexOf(i) >= n.length){
            let index = m.indexOf(i);
            m.splice(index, 1);
        }
    }
    return m;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([3, 6, 4, -2, 5]),[6, 4, -2, 6, 4, -2]);
}

test();
