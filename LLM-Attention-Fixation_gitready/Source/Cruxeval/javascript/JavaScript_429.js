function f(d){
    let result = [];
    while (Object.keys(d).length > 0) {
        let keys = Object.keys(d);
        let key = keys[keys.length - 1];
        result.push([key, d[key]]);
        delete d[key];
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({5: 1, "abc": 2, "defghi": 2, 87.29: 3}),[[87.29, 3], ["defghi", 2], ["abc", 2], [5, 1]]);
}

test();
