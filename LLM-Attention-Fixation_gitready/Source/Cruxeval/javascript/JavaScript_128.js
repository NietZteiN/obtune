function f(text){
    let odd = '';
    let even = '';
    for (let i = 0; i < text.length; i++) {
        if (i % 2 === 0) {
            even += text[i];
        } else {
            odd += text[i];
        }
    }
    return even + odd.toLowerCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Mammoth"),"Mmohamt");
}

test();
