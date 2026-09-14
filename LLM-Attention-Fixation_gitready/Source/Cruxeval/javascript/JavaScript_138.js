function f(text, chars){
    let listchars = chars.split('');
    let first = listchars.pop();
    for(let i of listchars){
        text = text.substring(0, text.indexOf(i)) + i + text.substring(text.indexOf(i) + 1);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("tflb omn rtt", "m"),"tflb omn rtt");
}

test();
