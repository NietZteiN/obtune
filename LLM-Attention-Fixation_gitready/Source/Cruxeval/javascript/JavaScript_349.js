function f(dictionary){
    dictionary[1049] = 55;
    var keys = Object.keys(dictionary);
    var lastKey = keys[keys.length - 1];
    var value = dictionary[lastKey];
    delete dictionary[lastKey];
    dictionary[lastKey] = value;
    return dictionary;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"noeohqhk": 623}),{"noeohqhk": 623, "1049": 55});
}

test();
