function f(text, search_string){
    let indexes = [];
    while (text.includes(search_string)) {
        indexes.push(text.lastIndexOf(search_string));
        text = text.substring(0, text.lastIndexOf(search_string));
    }
    return indexes;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ONBPICJOHRHDJOSNCPNJ9ONTHBQCJ", "J"),[28, 19, 12, 6]);
}

test();
