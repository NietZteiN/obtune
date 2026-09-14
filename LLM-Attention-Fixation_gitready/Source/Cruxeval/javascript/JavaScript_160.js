function f(dictionary){
    while (!dictionary.hasOwnProperty(1) || Object.keys(dictionary).length === 0) {
        dictionary = {};
        break;
    }
    return dictionary;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({1: 47698, 1: 32849, 1: 38381, 3: 83607}),{1: 38381, 3: 83607});
}

test();
