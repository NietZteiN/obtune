function f(my_dict){
    let result = {};
    for (let key in my_dict) {
        result[my_dict[key]] = key;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"a": 1, "b": 2, "c": 3, "d": 2}),{1: "a", 2: "d", 3: "c"});
}

test();
