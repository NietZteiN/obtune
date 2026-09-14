function f(array){
    if (array.length === 1) {
        return array.join('');
    }
    let result = array.slice();
    let i = 0;
    while (i < array.length - 1) {
        for (let j = 0; j < 2; j++) {
            result[i * 2] = array[i];
            i++;
        }
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["ac8", "qk6", "9wg"]),"ac8qk6qk6");
}

test();
