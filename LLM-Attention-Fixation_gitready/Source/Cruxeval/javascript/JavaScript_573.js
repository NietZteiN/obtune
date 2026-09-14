function f(string, prefix){
    if (string.startsWith(prefix)) {
        return string.substring(prefix.length);
    }
    return string;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Vipra", "via"),"Vipra");
}

test();
