function f(text, char){
    if (text) {
        if(text.startsWith(char)){
            text = text.slice(char.length);
        }
        if(text.endsWith(text.slice(-1).toLowerCase())){
            text = text.slice(0, -1) + text.slice(-1).toUpperCase();
        }
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("querist", "u"),"querisT");
}

test();
