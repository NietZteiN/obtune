function f(string){
    if (string.substring(0, 4) !== 'Nuva') {
        return 'no';
    } else {
        return string.trim();
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Nuva?dlfuyjys"),"Nuva?dlfuyjys");
}

test();
