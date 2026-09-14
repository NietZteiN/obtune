function f(ls, n){
    let answer = 0;
    for(let i of ls){
        if(i[0] === n){
            answer = i;
        }
    }
    return answer;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[1, 9, 4], [83, 0, 5], [9, 6, 100]], 1),[1, 9, 4]);
}

test();
