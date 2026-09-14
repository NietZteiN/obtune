function f(array, value){
    array.reverse();
    array.pop();
    var odd = [];
    while(array.length > 0){
        var tmp = {};
        tmp[array.pop()] = value;
        odd.push(tmp);
    }
    var result = {};
    while(odd.length > 0){
        Object.assign(result, odd.pop());
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["23"], 123),{});
}

test();
