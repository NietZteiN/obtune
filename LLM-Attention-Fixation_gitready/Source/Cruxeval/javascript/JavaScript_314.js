function f(text) {
    if (text.includes(',')) {
        let index = text.indexOf(',');
        let before = text.substring(0, index);
        let after = text.substring(index + 1);
        return after + ' ' + before;
    }
    let parts = text.split(' ');
    return ',' + parts[parts.length - 1] + ' 0';
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("244, 105, -90")," 105, -90 244");
}

test();
