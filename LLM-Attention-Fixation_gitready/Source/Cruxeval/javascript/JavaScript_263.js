function f(base, delta){
    for (let j = 0; j < delta.length; j++) {
        for (let i = 0; i < base.length; i++) {
            if (base[i] === delta[j][0]) {
                if (delta[j][1] !== base[i]) {
                    base[i] = delta[j][1];
                } else {
                    throw new Error('AssertionError: delta[j][1] must not be equal to base[i]');
                }
            }
        }
    }
    return base;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["gloss", "banana", "barn", "lawn"], []),["gloss", "banana", "barn", "lawn"]);
}

test();
