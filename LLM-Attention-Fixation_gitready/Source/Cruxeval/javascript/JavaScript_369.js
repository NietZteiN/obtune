function f(input){
    if (!isNaN(input)) {
        return "int";
    } else if (!isNaN(input.replace('.', ''))) {
        return "float";
    } else if (input.split(' ').length === input.length - 1) {
        return "str";
    } else if (input.length === 1) {
        return "char";
    } else {
        return "tuple";
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(" 99 777"),"tuple");
}

test();
