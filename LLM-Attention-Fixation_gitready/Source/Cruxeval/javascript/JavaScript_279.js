function f(text) {
    let ans = '';
    while (text !== '') {
        let [x, sep, rest] = text.partition('(');
        ans = x + sep.replace('(', '|') + ans;
        ans = ans + rest[0] + ans;
        text = rest.slice(1);
    }
    return ans;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(""),"");
}

test();
