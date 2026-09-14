function f(text){
    let x = 0;
    let ascii_a = 'a'.charCodeAt(0);
    let ascii_z = 'z'.charCodeAt(0);
    if (text === text.toLowerCase()) {
        for (let c of text) {
            let ascii_c = c.charCodeAt(0);
            if (ascii_c >= ascii_a && ascii_c <= ascii_z) {
                if (!isNaN(parseInt(c))) x+=1;
            }
        }
    }
    return x;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("591237865"),0);
}

test();
