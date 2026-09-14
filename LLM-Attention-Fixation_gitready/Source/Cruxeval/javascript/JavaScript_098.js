function f(s){
    return s.split(' ').reduce((acc, curr) => {
        return acc + (curr.charAt(0) === curr.charAt(0).toUpperCase() && curr.slice(1) === curr.slice(1).toLowerCase() ? 1 : 0);
    }, 0);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("SOME OF THIS Is uknowN!"),1);
}

test();
