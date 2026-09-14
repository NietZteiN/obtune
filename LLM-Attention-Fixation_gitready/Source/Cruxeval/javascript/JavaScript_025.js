function f(d){
    let newDict = Object.assign({}, d);
    delete newDict[Object.keys(newDict).pop()];
    return newDict;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"l": 1, "t": 2, "x:": 3}),{"l": 1, "t": 2});
}

test();
