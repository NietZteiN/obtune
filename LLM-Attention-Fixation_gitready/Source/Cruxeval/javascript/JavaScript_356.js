function f(array, num){
    let reverse = false;
    if (num < 0){
        reverse = true;
        num *= -1;
    }
    let newArray = array.slice().reverse().flat(num);
    
    if (reverse){
        newArray.reverse();
    }
    return newArray;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2], 1),[2, 1]);
}

test();
