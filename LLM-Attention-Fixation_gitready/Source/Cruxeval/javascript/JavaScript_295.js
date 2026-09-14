function f(fruits){
    if (fruits[fruits.length - 1] === fruits[0]) {
        return ['no'];
    } else {
        fruits.shift();
        fruits.pop();
        fruits.shift();
        fruits.pop();
        return fruits;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["apple", "apple", "pear", "banana", "pear", "orange", "orange"]),["pear", "banana", "pear"]);
}

test();
