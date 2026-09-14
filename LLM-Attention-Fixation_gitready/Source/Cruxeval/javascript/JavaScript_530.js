function f(s, ch){
    let sl = s;
    if (s.includes(ch)) {
        sl = s.replace(new RegExp('^' + ch + '+'), '');
        if (sl.length === 0) {
            sl = sl + '!?';
        }
    } else {
        return 'no';
    }
    return sl;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("@@@ff", "@"),"ff");
}

test();
