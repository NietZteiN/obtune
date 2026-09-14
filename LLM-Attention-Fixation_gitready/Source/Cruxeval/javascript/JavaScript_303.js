function f(text){
    let i = Math.floor((text.length + 1) / 2);
    let result = text.split('');
    while (i < text.length) {
        let t = result[i].toLowerCase();
        if (t === result[i]) {
            i++;
        } else {
            result[i] = t;
        }
        i += 2;
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mJkLbn"),"mJklbn");
}

test();
