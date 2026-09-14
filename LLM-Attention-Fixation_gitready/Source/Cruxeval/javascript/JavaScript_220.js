function f(text, m, n){
    text = text + text.substring(0, m) + text.substring(n);
    let result = "";
    for(let i = n; i < text.length - m; i++){
        result = text[i] + result;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abcdefgabc", 1, 2),"bagfedcacbagfedc");
}

test();
