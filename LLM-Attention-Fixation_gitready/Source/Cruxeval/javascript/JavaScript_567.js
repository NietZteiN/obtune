function f(s, n){
    let ls = s.split(' ');
    let out = [];
    while (ls.length >= n) {
        out = ls.splice(ls.length - n).concat(out);
    }
    return ls.concat(out.join('_'));
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("one two three four five", 3),["one", "two", "three_four_five"]);
}

test();
