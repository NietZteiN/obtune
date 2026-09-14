function f(lists){
    lists[1].length = 0;
    lists[2].push(...lists[1]);
    return lists[0];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([[395, 666, 7, 4], [], [4223, 111]]),[395, 666, 7, 4]);
}

test();
