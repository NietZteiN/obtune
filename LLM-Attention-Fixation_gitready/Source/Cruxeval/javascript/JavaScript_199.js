function f(s, char){
    let base = char.repeat(s.split(char).length) + char;
    return s.replace(new RegExp(base + '$'), '');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("mnmnj krupa...##!@#!@#$$@##", "@"),"mnmnj krupa...##!@#!@#$$@##");
}

test();
