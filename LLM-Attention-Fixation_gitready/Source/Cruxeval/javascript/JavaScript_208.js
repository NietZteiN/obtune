function f(items){
    let result = [];
    for(let item of items) {
        for(let d of item) {
            if(isNaN(parseInt(d))) {
                result.push(d);
            }
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["123", "cat", "d dee"]),["c", "a", "t", "d", " ", "d", "e", "e"]);
}

test();
