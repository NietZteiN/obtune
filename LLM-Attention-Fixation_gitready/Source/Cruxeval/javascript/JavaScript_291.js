function f(dictionary, arr) {
    dictionary[arr[0]] = [arr[1]];
    if (dictionary[arr[0]].length === arr[1]) {
        dictionary[arr[0]] = arr[0];
    }
    return dictionary;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}, ["a", 2]),{"a": [2]});
}

test();
