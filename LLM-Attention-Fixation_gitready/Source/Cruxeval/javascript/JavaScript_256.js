function f(text, sub){
    let a = 0;
    let b = text.length - 1;

    while (a <= b){
        let c = Math.floor((a + b) / 2);
        if (text.lastIndexOf(sub) >= c){
            a = c + 1;
        } else {
            b = c - 1;
        }
    }

    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("dorfunctions", "2"),0);
}

test();
