function f(nums){
    let digits = [];
    for(let num of nums){
        if((typeof num === 'string' && !isNaN(num)) || typeof num === 'number'){
            digits.push(num);
        }
    }
    digits = digits.map(element => parseInt(element));
    return digits;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([0, 6, "1", "2", 0]),[0, 6, 1, 2, 0]);
}

test();
