function f(names){
    if (names.length === 0) {
        return "";
    }
    let smallest = names[0];
    for (let i = 1; i < names.length; i++) {
        if (names[i] < smallest) {
            smallest = names[i];
        }
    }
    names.splice(names.indexOf(smallest), 1);
    return smallest;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),"");
}

test();
