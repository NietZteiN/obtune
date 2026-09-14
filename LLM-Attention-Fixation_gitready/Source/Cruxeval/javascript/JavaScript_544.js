function f(text) {
    let a = text.split('\n');
    let b = [];
    for (let i = 0; i < a.length; i++) {
        let c = a[i].replace(/\t/g, '    ');
        b.push(c);
    }
    return b.join('\n');
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`			tab tab tabulates`),"            tab tab tabulates");
}

test();
