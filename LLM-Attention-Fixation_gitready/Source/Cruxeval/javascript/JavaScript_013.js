function f(names){
    let count = names.length;
    let numberOfNames = 0;
    names.forEach(name => {
        if (/^[a-zA-Z]+$/.test(name)) {
            numberOfNames++;
        }
    });
    return numberOfNames;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["sharron", "Savannah", "Mike Cherokee"]),2);
}

test();
