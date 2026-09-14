function f(n, m, text){
    if (text.trim() === '') {
        return text;
    }
    let head = text[0];
    let mid = text.substring(1, text.length - 1);
    let tail = text[text.length - 1];
    let joined = head.replace(new RegExp(n, 'g'), m) + mid.replace(new RegExp(n, 'g'), m) + tail.replace(new RegExp(n, 'g'), m);
    return joined;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("x", "$", "2xz&5H3*1a@#a*1hris"),"2$z&5H3*1a@#a*1hris");
}

test();
