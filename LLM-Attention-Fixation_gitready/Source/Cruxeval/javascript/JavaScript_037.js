function f(text){
    let text_arr = [];
    for(let j = 0; j < text.length; j++) {
        text_arr.push(text.slice(j));
    }
    return text_arr;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("123"),["123", "23", "3"]);
}

test();
