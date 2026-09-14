function f(text, characters){
    let character_list = characters.split('') + [' ', '_'];

    let i = 0;
    while (i < text.length && character_list.includes(text[i])) {
        i++;
    }

    return text.slice(i);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("2nm_28in", "nm"),"2nm_28in");
}

test();
