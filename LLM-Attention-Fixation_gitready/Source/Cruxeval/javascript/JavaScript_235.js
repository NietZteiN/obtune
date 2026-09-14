function f(array, arr){
    let result = [];
    for (let s of arr) {
        result = result.concat(s.split(array[arr.indexOf(s)]).filter(l => l !== ''));
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([], []),[]);
}

test();
