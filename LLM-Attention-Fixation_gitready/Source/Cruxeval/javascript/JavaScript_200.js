function f(text, value){
    let length = text.length;
    let index = 0;
    while (length > 0){
        value = text[index] + value;
        length--;
        index++;
    }
    return value;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("jao mt", "house"),"tm oajhouse");
}

test();
