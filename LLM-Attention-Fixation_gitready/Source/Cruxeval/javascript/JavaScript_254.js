function f(text, repl){
    const trans = new Map([...text.toLowerCase()].map((char, index) => [char, repl.toLowerCase()[index] || char]));
    return [...text].map(char => trans.get(char)).join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("upper case", "lower case"),"lwwer case");
}

test();
