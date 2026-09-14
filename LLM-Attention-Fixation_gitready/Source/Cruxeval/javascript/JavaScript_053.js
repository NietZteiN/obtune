function f(text){
    let occ = {};
    for(let i = 0; i < text.length; i++){
        let ch = text[i];
        let name = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e', 'e': 'f'}[ch] || ch;
        occ[name] = (occ[name] || 0) + 1;
    }
    return Object.values(occ);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("URW rNB"),[1, 1, 1, 1, 1, 1, 1]);
}

test();
