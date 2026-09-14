function f(text){
    if (text && text === text.toUpperCase()) {
        let cs = Array.from(string.ascii_uppercase).reduce((acc, curr, idx) => {
            acc[curr] = string.ascii_lowercase[idx];
            return acc;
        }, {});
        return text.split('').map(c => cs[c] || c).join('');
    }
    return text.toLowerCase().slice(0, 3);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mTYWLMwbLRVOqNEf.oLsYkZORKE[Ko[{n"),"mty");
}

test();
