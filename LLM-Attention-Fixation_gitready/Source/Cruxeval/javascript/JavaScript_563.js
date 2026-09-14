function f(text1, text2){
    let nums = [];
    for(let i = 0; i < text2.length; i++){
        nums.push(text1.split(text2[i]).length - 1);
    }
    return nums.reduce((a, b) => a + b, 0);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("jivespdcxc", "sx"),2);
}

test();
