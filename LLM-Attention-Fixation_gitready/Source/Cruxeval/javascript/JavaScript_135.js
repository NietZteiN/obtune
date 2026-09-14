function f(){
    let d = {
        'Russia': ['Moscow', 'Vladivostok'],
        'Kazakhstan': ['Astana'],
    };
    return Object.keys(d);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(),["Russia", "Kazakhstan"]);
}

test();
