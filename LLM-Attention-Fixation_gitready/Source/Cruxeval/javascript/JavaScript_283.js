function f(dictionary, key){
    delete dictionary[key];
    let keys = Object.keys(dictionary);
    if (Math.min(...keys.map(k => parseInt(k))) === parseInt(key)) {
        key = keys[0];
    }
    return key;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"Iron Man": 4, "Captain America": 3, "Black Panther": 0, "Thor": 1, "Ant-Man": 6}, "Iron Man"),"Iron Man");
}

test();
