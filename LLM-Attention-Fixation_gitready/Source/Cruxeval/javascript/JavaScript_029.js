function f(text){
    let nums = text.split('').filter(char => /\d/.test(char));
    if (nums.length === 0) {
        throw new Error('The text does not contain any numbers');
    }
    return nums.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`-123   	+314`),"123314");
}

test();
