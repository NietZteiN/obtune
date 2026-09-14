function f(text, letter){
    let counts = {};
    for (let i = 0; i < text.length; i++) {
        if (!counts[text[i]]) {
            counts[text[i]] = 1;
        } else {
            counts[text[i]] += 1;
        }
    }
    return counts[letter] || 0;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("za1fd1as8f7afasdfam97adfa", "7"),2);
}

test();
