function f(text, sep, maxsplit){
    let splitted = text.split(sep, maxsplit + 1);
    let length = splitted.length;
    let new_splitted = splitted.slice(0, Math.floor(length / 2));
    new_splitted.reverse();
    new_splitted = new_splitted.concat(splitted.slice(Math.floor(length / 2)));
    return new_splitted.join(sep);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ertubwi", "p", 5),"ertubwi");
}

test();
