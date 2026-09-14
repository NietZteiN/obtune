function f(text){
    let ls = text.split('').reverse();
    let text2 = '';
    for (let i = ls.length - 3; i > 0; i -= 3) {
        text2 += ls.slice(i, i + 3).join('---') + '---';
    }
    return text2.slice(0, -3);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("scala"),"a---c---s");
}

test();
