function f(text, to_remove){
    let new_text = text.split('');
    if (new_text.includes(to_remove)) {
        let index = new_text.indexOf(to_remove);
        new_text.splice(index, 1, '?');
        new_text.splice(new_text.indexOf('?'), 1);
    }
    return new_text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("sjbrlfqmw", "l"),"sjbrfqmw");
}

test();
