function f(text) {
    let length = text.length;
    let index = 0;
    while (index < length && /\s/.test(text[index])) {
        index += 1;
    }
    return text.substring(index, index + 5);
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`-----	
	th
-----`),"-----");
}

test();
