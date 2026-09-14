function f(arr, d){
    for(let i = 1; i < arr.length; i += 2){
        d[arr[i]] = arr[i-1];
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["b", "vzjmc", "f", "ae", "0"], {}),{"vzjmc": "b", "ae": "f"});
}

test();
