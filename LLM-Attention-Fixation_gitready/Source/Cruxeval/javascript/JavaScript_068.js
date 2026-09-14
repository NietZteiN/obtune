function f(text, pref){
    if (text.startsWith(pref)){
        let n = pref.length;
        let textArr = text.substring(n).split('.');
        let newText = textArr.slice(1).concat(text.substring(0, n).split('.').slice(0, -1)).join('.');
        text = newText;
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("omeunhwpvr.dq", "omeunh"),"dq");
}

test();
