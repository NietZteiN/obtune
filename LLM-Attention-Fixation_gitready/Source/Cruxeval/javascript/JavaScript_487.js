function f(dict){
    let even_keys = [];
    for (let key in dict) {
        if (key % 2 === 0) {
            even_keys.push(parseInt(key));
        }
    }
    return even_keys;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({4: "a"}),[4]);
}

test();
