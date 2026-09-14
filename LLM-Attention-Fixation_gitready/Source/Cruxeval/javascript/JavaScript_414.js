function f(d){
    let dCopy = {...d};
    for (let key in dCopy) {
        let value = dCopy[key];
        for (let i = 0; i < value.length; i++) {
            value[i] = value[i].toUpperCase();
        }
    }
    return dCopy;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"X": ["x", "y"]}),{"X": ["X", "Y"]});
}

test();
