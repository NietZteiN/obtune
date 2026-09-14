function f(a){
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < a.length; j++) {
            if (a[j] !== '#') {
                a = a.substring(j);
                break;
            }
        }
        if (a === "") {
            break;
        }
    }
    while (a.slice(-1) === '#') {
        a = a.slice(0, -1);
    }
    return a;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("##fiu##nk#he###wumun##"),"fiu##nk#he###wumun");
}

test();
