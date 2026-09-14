function f(list_, num){
    let temp = [];
    for(let i of list_){
        i = Array(Math.floor(num / 2) + 1).join(i + ',');
        temp.push(i);
    }
    return temp;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["v"], 1),[""]);
}

test();
