function f(values, item1, item2){
    if (values[values.length - 1] === item2) {
        if (!values.slice(1).includes(values[0])) {
            values.push(values[0]);
        }
    } else if (values[values.length - 1] === item1) {
        if (values[0] === item2) {
            values.push(values[0]);
        }
    }
    return values;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 1], 2, 3),[1, 1]);
}

test();
