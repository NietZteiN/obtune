function f(phrase){
    let ans = 0;
    phrase.split().forEach((w) => {
        for (let ch of w) {
            if (ch === "0") {
                ans++;
            }
        }
    });
    return ans;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("aboba 212 has 0 digits"),1);
}

test();
