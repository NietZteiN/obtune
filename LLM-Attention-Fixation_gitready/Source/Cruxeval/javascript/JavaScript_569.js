function f(txt){
    let coincidences = {};
    for (let i = 0; i < txt.length; i++){
        let c = txt[i];
        if (coincidences[c]){
            coincidences[c] += 1;
        } else {
            coincidences[c] = 1;
        }
    }
    return Object.values(coincidences).reduce((acc, val) => acc + val, 0);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("11 1 1"),6);
}

test();
