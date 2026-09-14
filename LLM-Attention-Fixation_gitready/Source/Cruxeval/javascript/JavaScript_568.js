function f(num){
    let letter = 1;
    let digits = '1234567890';
    for (let i = 0; i < digits.length; i++) {
        num = num.replace(digits[i], '');
        if (num.length === 0) break;
        num = num.slice(letter) + num.slice(0, letter);
        letter++;
    }
    return num;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("bwmm7h"),"mhbwm");
}

test();
