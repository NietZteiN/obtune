function f(d){
    const sortedKeys = Object.keys(d).sort((a, b) => b - a);
    const key1 = parseInt(sortedKeys[0]);
    const val1 = d[key1];
    delete d[key1];
    const key2 = parseInt(sortedKeys[1]);
    const val2 = d[key2];
    delete d[key2];
    return {[key1]: val1, [key2]: val2};
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({2: 3, 17: 3, 16: 6, 18: 6, 87: 7}),{87: 7, 18: 6});
}

test();
