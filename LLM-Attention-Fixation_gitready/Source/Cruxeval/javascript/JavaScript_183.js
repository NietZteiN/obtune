function f(text){
    let ls = text.split(' ');
    let lines = ls.filter((_, index) => index % 3 === 0).join(' ').split('\n');
    let res = [];
    for (let i = 0; i < 2; i++) {
        let ln = ls.filter((_, index) => (index - 1) % 3 === 0);
        if (3 * i + 1 < ln.length) {
            res.push(ln.slice(3 * i, 3 * (i + 1)).join(' '));
        }
    }
    return lines.concat(res);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("echo hello!!! nice!"),["echo"]);
}

test();
