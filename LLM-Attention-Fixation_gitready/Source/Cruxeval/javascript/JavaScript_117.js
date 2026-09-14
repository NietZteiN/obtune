function f(numbers){
    for(let i = 0; i < numbers.length; i++){
        if(numbers.split('3').length - 1 > 1){
            return i;
        }
    }
    return -1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("23157"),-1);
}

test();
