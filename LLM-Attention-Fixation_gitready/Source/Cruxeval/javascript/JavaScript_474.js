function f(txt, marker) {
    let a = [];
    let lines = txt.split('\n');
    for (let line of lines) {
        a.push(line.padStart((line.length + marker) / 2).padEnd(marker));
    }
    return a.join('\n');
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`#[)[]>[^e>
 8`, -5),`#[)[]>[^e>
 8`);
}

test();
