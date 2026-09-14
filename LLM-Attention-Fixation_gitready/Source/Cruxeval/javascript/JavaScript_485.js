function f(tokens){
    tokens = tokens.split(' ');
    if (tokens.length === 2) {
        tokens.reverse();
    }
    let result = tokens[0].padEnd(5) + ' ' + tokens[1].padEnd(5);
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("gsd avdropj"),"avdropj gsd  ");
}

test();
