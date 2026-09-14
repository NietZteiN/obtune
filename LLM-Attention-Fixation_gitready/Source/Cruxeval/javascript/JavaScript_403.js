function f(full, part){
    let length = part.length;
    let index = full.indexOf(part);
    let count = 0;
    while (index >= 0){
        full = full.slice(index + length);
        index = full.indexOf(part);
        count++;
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("hrsiajiajieihruejfhbrisvlmmy", "hr"),2);
}

test();
