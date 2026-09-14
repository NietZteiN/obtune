function f(string, code){
    let t = '';
    try {
        t = new TextEncoder().encode(string, { "stream": true });
        if (t[t.length - 1] === 10) {
            t.pop();
        }
        t = new TextDecoder().decode(t);
        return t;
    } catch (error) {
        return t;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("towaru", "UTF-8"),"towaru");
}

test();
