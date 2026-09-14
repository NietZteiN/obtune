function f(text, lower, upper){
    let count = 0;
    let new_text = [];
    for (let char of text) {
        char = char.match(/\d/) ? lower : upper;
        if (char === 'p' || char === 'C') {
            count++;
        }
        new_text.push(char);
    }
    return [count, new_text.join('')];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("DSUWeqExTQdCMGpqur", "a", "x"),[0, "xxxxxxxxxxxxxxxxxx"]);
}

test();
