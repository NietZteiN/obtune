function f(pattern, items){
    let result = [];
    items.forEach(text => {
        let pos = text.lastIndexOf(pattern);
        if (pos >= 0) {
            result.push(pos);
        }
    });
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(" B ", [" bBb ", " BaB ", " bB", " bBbB ", " bbb"]),[]);
}

test();
