function f(number){
    let transl = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5};
    let result = [];
    for (let key in transl) {
        let value = transl[key];
        if (value % number === 0) {
            result.push(key);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(2),["B", "D"]);
}

test();
