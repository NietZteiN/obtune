function f(mylist){
    let revl = mylist.slice();
    revl.reverse();
    mylist.sort((a, b) => b - a);
    return JSON.stringify(mylist) === JSON.stringify(revl);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([5, 8]),true);
}

test();
