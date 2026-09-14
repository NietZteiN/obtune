function f(text, delimiter){
    let partition = text.split(delimiter);
    return partition.slice(0, -1).join(delimiter);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("xxjarczx", "x"),"xxjarcz");
}

test();
