function f(text, a, b){
    text = text.replace(new RegExp(a, 'g'), b);
    return text.replace(new RegExp(b, 'g'), a);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(" vup a zwwo oihee amuwuuw! ", "a", "u")," vap a zwwo oihee amawaaw! ");
}

test();
