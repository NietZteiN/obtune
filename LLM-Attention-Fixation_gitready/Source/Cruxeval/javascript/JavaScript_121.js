function f(s){
    let nums = s.split('').filter(c => !isNaN(c)).join('');
    if(nums === ''){
        return 'none';
    }
    let m = Math.max(...nums.split(',').map(num => parseInt(num)));
    return m.toString();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("01,001"),"1001");
}

test();
