function f(array){
    let c = array
    let array_copy = array

    while (true) {
        c.push('_');
        if (JSON.stringify(c) === JSON.stringify(array_copy)) {
            array_copy[c.indexOf('_')] = '';
            break;
        }
    }
    return array_copy;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[""]);
}

test();
