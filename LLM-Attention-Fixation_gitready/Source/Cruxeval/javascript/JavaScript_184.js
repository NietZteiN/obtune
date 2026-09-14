function f(digits){
    digits.reverse();
    if (digits.length < 2) {
        return digits;
    }
    for (let i = 0; i < digits.length; i += 2) {
        [digits[i], digits[i+1]] = [digits[i+1], digits[i]];
    }
    return digits;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2]),[1, 2]);
}

test();
